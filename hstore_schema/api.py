from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from hstore_schema.models import Bucket, Dataset, Field, Record, Revision
from hstore_schema.serializers import (BucketSerializer, DatasetSerializer,
        RecordSerializer, RevisionSerializer)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'buckets': reverse('bucket_list', request=request),
        'datasets': reverse('dataset_list', request=request),
        'fields': reverse('field_list', request=request),
        'records': reverse('record_list', request=request),
    })


class BucketList(generics.ListAPIView):
    model = Bucket
    serializer_class = BucketSerializer


class BucketDetail(generics.RetrieveAPIView):
    model = Bucket
    serializer_class = BucketSerializer


class DatasetList(generics.ListAPIView):
    model = Dataset
    serializer_class = DatasetSerializer


class DatasetDetail(generics.RetrieveAPIView):
    model = Dataset
    serializer_class = DatasetSerializer


class RecordList(generics.ListAPIView):
    model = Record


class FieldList(generics.ListAPIView):
    model = Field


class RevisionDetail(generics.RetrieveAPIView):
    model = Revision
    serializer_class = RevisionSerializer
