from functools import wraps


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
        self._facet = None
        self._data = {}

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


class Registry(dict):
    def __init__(self, slug):
        self.slug = slug
        registries[slug] = self

    def register(self, slug, version=None):
        library = Library(slug, version)
        self[library.full_slug] = library
        return library

    def get(self, slug, version=None):
        full_slug = make_full_slug(slug, version)
        return self[full_slug]
