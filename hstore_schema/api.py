import json

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from hstore_schema.models import Bucket, Dataset, Record


class Resource(View):
    limit = 100

    def get(self, request, *args, **kwargs):
        qs = self.get_query_set(request, *args, **kwargs)
        if self.limit:
            qs = qs[:self.limit]
        content = serializers.serialize('json', qs)
        return HttpResponse(content, content_type='application/json')


class BucketListResource(Resource):
    limit = None

    def get_query_set(self, request, *args, **kwargs):
        return Bucket.objects.all()


class DatasetListResource(Resource):
    limit = None

    def get_query_set(self, request, bucket_slug, **kwargs):
        return (Dataset.revisions
                .current().filter(bucket__slug=bucket_slug)
                .select_related('source'))



class DatasetResource(Resource):
    def get_dataset(self):
        return (Dataset.revisions.current()
                .get(bucket__slug=self.kwargs.get('bucket_slug'),
                     slug=self.kwargs.get('dataset_slug'),
                     version=self.kwargs.get('version')))


class RecordListResource(DatasetResource):
    def get_query_set(self, request, bucket_slug, dataset_slug, version):
        dataset = self.get_dataset()
        return dataset.records.all()


class DatasetFieldListResource(DatasetResource):
    def get_query_set(self, request, bucket_slug, dataset_slug, version):
        dataset = self.get_dataset()
        return dataset.fields.all()
