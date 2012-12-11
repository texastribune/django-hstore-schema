import json
import urllib

from django.conf.urls import patterns, url
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template.defaultfilters import slugify
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


##
# Mixins
class FullReverseMixin(object):
    def full_reverse(self, name, args=None, kwargs=None, parameters=None):
        url = reverse(name, args=args, kwargs=kwargs)
        if name == self.name:
            parameters = parameters or {}
            get_parameters = dict(self.request.GET.items())
            parameters = dict(get_parameters, **parameters)
        if parameters:
            url = u'%s?%s' % (url, urllib.urlencode(parameters))
        return self.request.build_absolute_uri(url)


class PaginatorMixin(object):
    """
    Overrides the `get_data` method to paginate the object list.

    This may not be appropriate as a mixin because it relies on the base
    class returning a queryset from the `get_data` method.
    """
    def __init__(self, **kwargs):
        self.limit = kwargs.pop('limit', 20)
        super(PaginatorMixin, self).__init__(**kwargs)

    def get_int_parameter(self, var, default=None, positive=False):
        try:
            value = int(self.request.GET.get(var, default))
        except ValueError:
            raise APIError('"%s" must be a valid number' % var)

        if positive and value <= 0:
            raise APIError('"%s" must be a number greater than zero' % var)

        return value

    def get_data(self):
        # Try to get the current page number and limit from the request
        limit = self.get_int_parameter(
            'limit', default=self.limit, positive=True)
        page_number = self.get_int_parameter('page', default=1, positive=True)

        # Build the current page and raise a 404 if it does not exist
        data = super(PaginatorMixin, self).get_data()
        paginator = Paginator(data, limit)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            raise Http404

        # Build meta resource data
        meta = {'limit': limit,
                'page': page_number,
                'next': None,
                'previous': None,
                'count': data.count()}

        # Build the full next and previous URLs
        if page.has_next():
            meta['next'] = self.full_reverse(self.name, kwargs=self.kwargs,
                parameters={'page': page.next_page_number()})
        if page.has_previous():
            meta['previous'] = self.full_reverse(self.name, kwargs=self.kwargs,
                parameters={'page': page.previous_page_number()})

        return {'meta': meta, 'data': page.object_list}

    def marshal_data(self, data):
        marshaled_data = super(PaginatorMixin, self).marshal_data(data['data'])
        return dict(data, data=marshaled_data)


class SlugFilterMixin(object):
    def get_filters(self):
        filters = super(SlugFilterMixin, self).get_filters()
        if 'slug' in self.request.GET:
            filters['slug'] = self.request.GET['slug']

        return filters


##
# Resources
class Resource(FullReverseMixin, View):
    content_type = 'application/json'

    name = None
    slug = None
    data = None
    pattern = None

    def __init__(self, name=None, slug=None, data=None, pattern=None):
        if name is not None:
            self.name = name
        if data is not None:
            self.data = data
        if not self.slug:
            self.slug = slug or self.name
        if not self.pattern:
            self.pattern = pattern or r'^%s/$' % self.slug

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
        self._serializer = PythonSerializer()

        model = kwargs.pop('model', None)
        slug = kwargs.pop('slug', None)
        if model is not None:
            self.model = model
        if slug is None:
            kwargs['slug'] = slugify(self.model._meta.verbose_name_plural)

        super(ModelResource, self).__init__(**kwargs)

    def get_urls(self):
        name = self.name or self.model.verbose_name
        view = self.__class__.as_view(
            model=self.model, name=self.name, slug=self.slug)
        return [url(self.pattern, view, name=name)]

    def get_query_set(self):
        return self.model.objects.all()

    def get_data(self):
        return self.get_query_set()

    def marshal_object(self, obj):
        return self._serializer.serialize([obj])[0]['fields']

    def marshal_data(self, data):
        return [self.marshal_object(obj) for obj in data]


class ModelListResource(PaginatorMixin, ModelResource):
    def __init__(self, **kwargs):
        super(ModelListResource, self).__init__(**kwargs)
        if not self.name:
            self.name = '%s_list' % self.model._meta.verbose_name

    def get_filters(self):
        """
        Returns a filter spec that will be passed to the queryset.
        """
        return {}

    def get_query_set(self):
        filters = self.get_filters()
        return super(ModelListResource, self).get_query_set().filter(**filters)


class ModelDetailResource(ModelResource):
    def __init__(self, **kwargs):
        super(ModelDetailResource, self).__init__(**kwargs)
        if not self.name:
            self.name = '%s_detail' % self.model._meta.verbose_name
        self.pattern = '%s/(?P<pk>\d+)/$' % self.pattern.rstrip('/$')

        self.related_resources = {}

    def get_data(self):
        return self.get_query_set().get(pk=self.kwargs['pk'])

    def marshal_object(self, obj):
        data = super(ModelDetailResource, self).marshal_object(obj)
        for attr, resource in self.related_resources.items():
            data[attr] = self.full_reverse(self.name, kwargs={'pk': self.pk})
        return data

    def marshal_data(self, data):
        return self.marshal_object(data)

    def __getattr__(self, attr):
        # If the attr is a related field from this resource's model,
        # build a related resource with this resource's arguments in the
        # queryset filter.
        model_attr = getattr(self.model, attr, None)
        if model_attr and hasattr(model_attr, 'related'):
            try:
                return self.related_resources[attr]
            except KeyError:
                pass

            related_model = model_attr.related.model
            parent_attr = model_attr.related.field.name

            def get_filters(self):
                filters = super(self.__class__, self).get_filters()
                filters['%s__pk' % parent_attr] = self.kwargs['pk']
                return filters

            name = '%s_%s_list' % (parent_attr, attr)
            pattern = '%s/%s' % (self.pattern.rstrip('/$'), attr)
            resource = type('ModelListResource_%s' % name,
                            (ModelListResource,), {'get_filters': get_filters})
            self.related_resources[attr] = resource
            return resource(model=related_model, name=name, pattern=pattern)

        return super(ModelDetailResource, self).__getattribute__(attr)


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
    pattern = r'^$'

    def __init__(self, **kwargs):
        super(RootResource, self).__init__(**kwargs)

    def get_data(self):
        return {
            'buckets': self.full_reverse('bucket_list'),
            'datasets': self.full_reverse('dataset_list'),
            'records': self.full_reverse('record_list'),
            'fields': self.full_reverse('field_list'),
        }


class DatasetMixin(object):
    model = Dataset

    def marshal_object(self, obj):
        data = super(DatasetMixin, self).marshal_object(obj)
        data['records'] = self.full_reverse(
            'dataset_records_list', kwargs={'pk': obj.pk})
        data['fields'] = self.full_reverse(
            'dataset_fields_list', kwargs={'pk': obj.pk})
        return data


class DatasetListResource(DatasetMixin, ModelListResource):
    pass


class DatasetDetailResource(DatasetMixin, ModelDetailResource):
    pass
