from collections import defaultdict

from hstore_schema.models import Data

MAP_FIELDS = ['key', 'field', 'source', 'version']
GROUP_FIELDS = ['key', 'field', 'source', 'version']
REDUCE_FIELDS = ['key', 'source', 'version']

class MapReduce(object):
	def __init__(self):
		self.sources = set()
		self.mappers = {}
		self.reducers = {}

	def map(self, source, version=None, field=None):
		self.sources.add(source)
		key = (source, version, field)
		def wrap(function):
			self.mappers[key] = function
			def wrapped(value, **kwargs):
				return function(value, **kwargs)
		return wrap

	def reduce(self, source, version=None, field=None):
		key = (source, version, field)
		def wrap(function):
			self.reducers[key] = function
			def wrapped(values, **kwargs):
				return function(values, **kwargs)
		return wrap

	def run(self):
		mapped_data = self._map()
		grouped_data = self._group(mapped_data)
		reduced_data = self._reduce(grouped_data)
		for data in reduced_data:
			data.save()

	def _map(self):
		"""
		Maps existing (key, field, source, version, value) data to zero
		or more new (key, field, source, version, value) data.
		"""
		mapped_data = []
		qs = (Data.objects
			  .filter(source__in=self.sources)
			  .values_list('key', 'source', 'version', 'data'))
		for key, source, version, data in qs:
			# Get default mappers for this source and version
			source_key = (source, None, None)
			version_key = (source, version, None)
			if version_key in self.mappers:
				default_mapper = self.mappers[version_key]
			elif source_key in self.mappers:
				default_mapper = self.mappers[source_key]

			# Iterate over all data fields and apply mappers
			for field, value in data.iteritems():
				kwargs = dict(key=key, field=field, source=source,
							  version=version)

				# Use a version-specific field mapper if available...
				version_field_key = (key, source, version, field)
				if version_field_key in self.mappers:
					field_mapper = self.mappers[version_field_key]
					mapped_data.extend(field_mapper(value, **kwargs))
					continue

				# Then fall back to a source-specific field mapper...
				source_field_key = (source, None, field)
				if source_field_key in self.mappers:
					field_mapper = self.mappers[source_field_key]
					mapped_data.extend(field_mapper(value, **kwargs))
					continue

				# Finally fall back to the default mapper
				mapped_data.extend(default_mapper(value, **kwargs))

		return mapped_data

	def _group(self, mapped_data):
		"""
		Create mapping of (key, field, source, version) to values.
		"""
		grouped_data = defaultdict(list)
		for data in mapped_data:
			group_key = tuple(map(data.get, GROUP_FIELDS))
			grouped_data[group_key].append(data['value'])

		return grouped_data

	def _reduce(self, grouped_data):
		"""
		Aggregate new data values by (key, source, version).
		"""
		reduced_data = {}
		for group_key, values in grouped_data.iteritems():
			# Try to get the most specific reducer first
			key_dict = dict(zip(GROUP_FIELDS, group_key))
			reducer_keys = [
				(key_dict['source'], key_dict['version'], key_dict['field']),
				(key_dict['source'], key_dict['version'], None),
				(key_dict['source'], None, None),
			]

			# Get or create Data for this reduce key
			reduce_key = tuple(map(key_dict.get, REDUCE_FIELDS))
			try:
				data = reduced_data[reduce_key]
			except KeyError:
				data_kwargs = key_dict.copy()
				del data_kwargs['field']
				data = Data(**data_kwargs)
				reduced_data[reduce_key] = data

			# Aggregate field values in new Data
			for reducer_key in reducer_keys:
				if reducer_key in self.reducers:
					reducer = self.reducers[reducer_key]
					reducer(data, values, **key_dict)
					break

		return reduced_data.values()
