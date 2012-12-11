from functools import wraps
import re


registries = {}


def make_full_slug(slug, version):
    if version:
        return '%s/%s' % (slug, version)
    else:
        return slug


class Library(object):
    """
    Encapsulates the operations on a subset of data within a bucket.
    """
    def __init__(self, slug, version=None):
        self.slug = slug
        self.version = version

        self._key = None
        self._facets = {}
        self._field_data = {}

    @property
    def full_slug(self):
        return make_full_slug(self.slug, self.version)

    def key(self, namespace, keyspace=None):
        def wrapper(function):
            @wraps(function)
            def inner(record):
                key = function(record)
                return u'%s/%s' % (namespace, key)

            self._key = inner
            return inner

        return wrapper

    def facet(self, slug, required=False):
        def wrapper(function):
            @wraps(function)
            def inner(record, field, value):
                facet = function(record, field, value)
                if required is True and facet is None:
                    raise ValueError('Facet "%s" is required.' % slug)
                return facet

            self._facets[slug] = inner
            return function

        return wrapper

    def field_data(self, namespace, label=None, pattern=None):
        if pattern is not None:
            pattern = re.compile(pattern)

        def wrapper(function):
            @wraps(function)
            def inner(record):
                for field, value in record.data.iteritems():
                    if pattern and not pattern.match(field):
                        continue

                    if self._facets:
                        facets = {}
                        for slug, facet_func in self._facets.items():
                            facets[slug] = facet_func(record, field, value)
                    else:
                        facets = None

                    data = function(record, field, value, facets=facets)
                    if data:
                        data['source'] = {'field': field, 'value': value}
                        yield data

            slug = '%s/%s' % (namespace, inner.func_name)
            self._field_data[slug] = inner
            return function

        return wrapper

    def process(self, record):
        if self._key:
            key = self._key(record)
        else:
            key = None
        for label, f in self._field_data.iteritems():
            for kwargs in f(record):
                if kwargs:
                    print u'%s/%s' % (repr(key), label)
                    print kwargs


class Registry(dict):
    def __init__(self, slug):
        self.slug = slug
        registries[slug] = self

    def register(self, slug, version=None):
        library = Library(slug, version)
        self[library.full_slug] = library
        return library

    def get(self, slug, default=None, version=None):
        full_slug = make_full_slug(slug, version)
        return super(Registry, self).get(full_slug, default)
