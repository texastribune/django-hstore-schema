import urllib

from django.core.urlresolvers import reverse
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import Resource, ModelResource

from hstore_schema.models import *


class ReadOnlyJSONResource(ModelResource):
    class Meta:
        allowed_methods = ['get']

    def create_response(self, request, data, *args, **kwargs):
        meta = getattr(data, 'meta', None)
        if meta:
            host = request.get_host()
            next = meta.get('next')
            if next:
                meta['next'] = u'http://%s%s' % (host, meta['next'])
            previous = meta.get('previous')
            if previous:
                meta['previous'] = u'http://%s%s' % (host, meta['previous'])

        return (super(ReadOnlyJSONResource, self)
                .create_response(request, data, *args, **kwargs))

    def determine_format(self, request):
        return 'application/json'

    def dehydrate(self, bundle):
        host = bundle.request.get_host()
        for key in bundle.data:
            if key.endswith('_uri'):
                # key = key.replace('_uri', '_url')
                bundle.data[key] = 'http://%s%s' % (host, bundle.data[key])
        return bundle

    def reverse_dataset_url(self, name, dataset, **kwargs):
        kwargs.update(api_name=self._meta.api_name)
        url = reverse(name, kwargs=kwargs)
        parameters = urllib.urlencode({
            'dataset__bucket__slug': dataset.bucket.slug,
            'dataset__slug': dataset.slug,
            'dataset_version': dataset.version
        })
        return u'%s?%s' % (url, parameters)


class RootResource(ReadOnlyJSONResource):
    class Meta:
        pass

    def get_list(self):
        return {
            'buckets_uri': reverse('bucket_list', request=request),
            'datasets_uri': reverse('dataset_list', request=request),
            'fields_uri': reverse('field_list', request=request),
            'records_uri': reverse('record_list', request=request),
        }


class BucketResource(ReadOnlyJSONResource):
    class Meta:
        queryset = Bucket.objects.all()
        resource_name = 'buckets'
        filtering = {
            'slug': ('exact',),
        }


class DatasetResource(ReadOnlyJSONResource):
    bucket = fields.ForeignKey(BucketResource, 'bucket')

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'datasets'
        filtering = {
            'slug': ('exact',),
            'bucket': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['records_uri'] = self.reverse_dataset_url(
            'api_dispatch_list', bundle.obj, resource_name='records')
        bundle.data['fields_uri'] = self.reverse_dataset_url(
            'api_dispatch_list', bundle.obj, resource_name='fields')

        return super(DatasetResource, self).dehydrate(bundle)


class DatasetRelatedResource(ReadOnlyJSONResource):
    class Meta:
        filtering = {
            'dataset__slug': ('exact',),
            'dataset__version': ('exact',),
            'dataset__bucket__slug': ('exact',)
        }


class RecordResource(DatasetRelatedResource):
    class Meta:
        queryset = Record.objects.select_related()
        resource_name = 'records'

    def dehydrate(self, bundle):
        bundle.data['_key'] = bundle.obj._key
        bundle.data['_data'] = bundle.obj._data
        return super(RecordResource, self).dehydrate(bundle)

    def dehydrate_data(self, bundle):
        return bundle.obj.data


class FieldResource(DatasetRelatedResource):
    dataset_uri = fields.ForeignKey(DatasetResource, 'dataset')

    class Meta:
        queryset = Field.objects.all()
        resource_name = 'fields'
        excludes = ('id',)
        filtering = {
            'dataset': ALL_WITH_RELATIONS,
        }
