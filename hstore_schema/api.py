from django.core.urlresolvers import reverse
from tastypie import fields
from tastypie import serializers
from tastypie.resources import Resource, ModelResource

from hstore_schema.models import *


class ReadOnlyJSONResource(ModelResource):
    class Meta:
        allowed_methods = ['get']

    def determine_format(self, request):
        return 'application/json'


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


class DatasetResource(ReadOnlyJSONResource):
    bucket = fields.ForeignKey(BucketResource, 'bucket')

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'datasets'

    def dehydrate(self, bundle):
        records_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': 'records',
            'bucket_slug': bundle.obj.bucket.slug,
            'dataset_slug': bundle.obj.slug,
            'version': bundle.obj.version,
        })
        bundle.data['records'] = records_uri

        fields_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': 'fields',
            'bucket_slug': bundle.obj.bucket.slug,
            'dataset_slug': bundle.obj.slug,
            'version': bundle.obj.version,
        })
        bundle.data['fields'] = fields_uri
        return bundle


class DatasetRelatedResource(ReadOnlyJSONResource):
    def dispatch(self, *args, **kwargs):
        bucket_slug = kwargs.pop('bucket_slug', None)
        dataset_slug = kwargs.pop('dataset_slug', None)
        version = kwargs.pop('version', None)
        kwargs['dataset'] = (Dataset.revisions.current()
                             .get(bucket__slug=bucket_slug,
                                  slug=dataset_slug,
                                  version=version))
        return super(DatasetRelatedResource, self).dispatch(*args, **kwargs)


class RecordResource(DatasetRelatedResource):
    dataset = fields.ForeignKey(DatasetResource, 'dataset')

    class Meta:
        queryset = Record.objects.all()
        resource_name = 'records'
        filtering = {
            'dataset': ('exact',)
        }

    def dehydrate_data(self, bundle):
        return bundle.obj.data


class FieldResource(DatasetRelatedResource):
    class Meta:
        queryset = Field.objects.all()
        resource_name = 'fields'
        excludes = ('id',)
        filtering = {
            'dataset': ('exact',)
        }
