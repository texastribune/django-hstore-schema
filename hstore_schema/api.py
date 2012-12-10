import json
import urllib

from django.conf.urls import patterns, url
from django.core.paginator import Paginator
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View

from hstore_schema.models import *

##
# REST Framework
class APIError(Exception):
    pass


class API(object):
    def __init__(self, name):
        self.name = name
        self.urls = []

    def register(self, resource):
        self.urls += resource.get_urls()


class FullReverseMixin(object):
    def full_reverse(self, name, args=None, kwargs=None, parameters=None):
        url = reverse(name, args=args, kwargs=kwargs)
        return self.request.build_absolute_uri(url)


class PaginatorMixin(object):
    def __init__(self, **kwargs):
        self.limit = kwargs.pop('limit', 20)
        super(PaginatorMixin, self).__init__(**kwargs)

    def get_int_parameter(self, var, default=None, positive=False):
        try:
            value = int(self.request.GET.get(var, default))
        except ValueError:
            raise ApiError('%s must be a valid number')

        if positive and value <= 0:
            raise ApiError('%s must be a number greater than zero')

        return value

    def get_data(self):
        limit = self.get_int_parameter(
            'limit', default=self.limit, positive=True)
        page_number = self.get_int_parameter('page', default=1, positive=True)

        data = super(PaginatorMixin, self).get_data()
        paginator = Paginator(data, limit)
        page = paginator.page(page_number)
        meta = {'limit': limit,
                'page': page_number,
                'next': None,
                'previous': None,
                'count': data.count()}
        if page.has_next():
            meta['next'] = '?page=#TODO'
        if page.has_previous():
            meta['previous'] = '?page=#TODO'

        return {'meta': meta, 'data': page.object_list}

    def marshal_data(self, data):
        data['data'] = (super(PaginatorMixin, self)
                        .marshal_data(data['data']))
        return data


class Resource(FullReverseMixin, View):
    content_type = 'application/json'

    name = None
    slug = None
    data = None

    def __init__(self, name=None, slug=None, data=None):
        if name is not None:
            self.name = name
        if data is not None:
            self.data = data
        if not self.slug:
            self.slug = slug or self.name
        self.pattern = r'^%s/$' % self.slug

    def get(self, request, **kwargs):
        try:
            data = self.get_data()
            marshaled_data = self.marshal_data(data)
            serialized_data = self.serialize_data(marshaled_data)
            status_code = 200
        except APIError as e:
            serialized_data = json.dumps({"error": str(e)})
            status_code = 401

        return HttpResponse(content=serialized_data, status=status_code,
                            content_type=self.content_type)

    def get_urls(self):
        return [url(self.pattern, self.__class__.as_view(), name=self.name)]

    def get_data(self):
        return self.data

    def marshal_data(self, data):
        return data

    def serialize_data(self, data):
        return json.dumps(data)


class ModelResource(Resource):
    model = None

    def __init__(self, **kwargs):
        model = kwargs.pop('model', None)
        super(ModelResource, self).__init__(**kwargs)
        if model is not None:
            self.model = model
        if not self.name:
            self.name = self.model._meta.verbose_name
        self._serializer = PythonSerializer()

    def get_urls(self):
        slug = self.model._meta.verbose_name
        pattern = r'^%s/$' % slug
        name = self.name or self.model.verbose_name
        view = self.__class__.as_view(
            model=self.model, name=self.name, slug=self.slug)
        return [url(pattern, view, name=name)]

    def get_query_set(self):
        return self.model.objects.all()

    def get_data(self):
        return self.get_query_set()

    def marshal_object(self, obj):
        return self._serializer.serialize([obj])[0]['fields']

    def marshal_data(self, data):
        return [self.marshal_object(obj) for obj in data]


class ModelListResource(PaginatorMixin, ModelResource):
    def get_filters(self):
        """
        Returns a filter spec that will be passed to the queryset.
        """
        return {}

    def get_queryset(self, **filters):
        return self.get_query_set().filter(**filters)


class ModelDetailResource(ModelResource):
    def get_data(self, request, pk):
        filters = self.get_filters()
        return self.get_query_set(**filters).get(pk=pk)

    def marshal_data(self, data):
        return self.marshal_object(data)


##
# HSTORE schema resources
class DatasetRelatedResource(ModelListResource):
    def get_filters(self):
        filters = {}
        if 'dataset' in self.request.GET:
            filters['dataset__slug'] = self.request.GET['dataset']
        if 'bucket' in self.request.GET:
            filters['dataset__bucket__slug'] = self.request.GET['bucket']
        if 'version' in self.request.GET:
            filters['dataset__version'] = self.request.GET['version']
        if 'source' in self.request.GET:
            filters['dataset__source__slug'] = self.request.GET['source']

        return filters


class RootResource(Resource):
    name = 'root'
    url_pattern = r'^$'

    def __init__(self, **kwargs):
        super(RootResource, self).__init__(**kwargs)

    def get_data(self):
        return {
            'buckets_uri': self.full_reverse('root'),
            'datasets_uri': self.full_reverse('root'),
            'fields_uri': self.full_reverse('root'),
            'records_uri': self.full_reverse('root'),
        }


class BucketListResource(ModelListResource):
    model = Bucket
    name = 'bucket_list'
    url_pattern = r'^buckets/$'

    def get_filters(self):
        if 'slug' in self.request.GET:
            return {'slug': self.request.GET['slug']}
        else:
            return {}


class DatasetResource(ModelListResource):
    def marshal_object(self, obj):
        data = super(DatasetResource, self).marshal_object(obj)
        data['records_uri'] = '#TODO'
        data['fields_uri'] = '#TODO'
        return data
