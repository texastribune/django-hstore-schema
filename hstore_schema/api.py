from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from hstore_schema.models import (Bucket, Dataset, Field, Record, Revision,
        Source)
from hstore_schema.serializers import (BucketSerializer, DatasetSerializer,
        FieldSerializer, RecordSerializer, RevisionSerializer)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'buckets': reverse('bucket-list', request=request),
        'datasets': reverse('dataset-list', request=request),
        'fields': reverse('field-list', request=request),
        'records': reverse('record-list', request=request),
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
    serializer_class = FieldSerializer


class RevisionDetail(generics.RetrieveAPIView):
    model = Revision
    serializer_class = RevisionSerializer


class SourceDetail(generics.RetrieveAPIView):
    model = Source
