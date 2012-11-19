from rest_framework.serializers import HyperlinkedModelSerializer

from hstore_schema.models import Bucket, Dataset, Record, Field, Revision


class BucketSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Bucket
        fields = ('name', 'short_name', 'slug',)


class DatasetSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = ('revision', 'version', 'source', 'name', 'slug',)


class RevisionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Revision
        fields = ('digest', 'previous', 'timestamp',)


class RecordSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = ('dataset', 'key', 'data', 'label', 'order',)


class FieldSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Field
        fields = ('dataset', 'label', 'order', 'name',)
