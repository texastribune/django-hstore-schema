import uuid

from django.db import models
from django_hstore import hstore
import jsonfield



class Bucket(models.Model):
    """
    A namespace for data uniquely identified by its `slug`.
    """
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Namespace(models.Model):
    """
    Represents a type of entity like 'campus' or 'district'.
    """
    bucket = models.ForeignKey(Bucket, related_name='namespaces')

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        unique_together = ('bucket', 'slug')


class Source(models.Model):
    """
    A named source of data with some simple metadata.
    """
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    readme = models.TextField(blank=True, null=True)
    attribution = models.CharField(max_length=255, blank=True, null=True)


class Revision(models.Model):
    """
    A version of dataset that contains the sets of `Data` and `Record`s
    as they existed at particular time.

    The revision with no `next` revision contains the current dataset.

    `digest` is a UUID4 that is shared between all revisions that are
    run as part of the same process.
    """
    digest = models.CharField(max_length=32)
    next = models.OneToOneField('self', null=True, related_name='previous')

    def save(self, *args, **kwargs):
        if not self.digest:
            self.digest = uuid.uuid4()

        super(Revision, self).save(*args, **kwargs)

    @property
    def time(self):
        return uuid.UUID(self.digest).time


class RevisionManager(models.Manager):
    def current(self):
        return self.get_query_set().filter(revision__next__isnull=True)


class Dataset(models.Model):
    """
    A named set of data that is sourced from raw files.
    """
    bucket = models.ForeignKey(Bucket, related_name='datasets')

    revisions = RevisionManager()
    revision = models.ForeignKey(Revision, related_name='datasets')
    version = models.CharField(max_length=255)

    source = models.ForeignKey(Source, related_name='datasets')

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    raw = models.FileField(upload_to='datasets', blank=True, null=True)

    class Meta:
        unique_together = ('bucket', 'slug', 'revision')


class Record(models.Model):
    """
    Stores a raw record of data from a data source, such as a row from
    a CSV file or a JSON object.

    `data`: a dictionary of values keyed by the raw header
    `order`: the row number or list index in the raw file
    """
    dataset = models.ForeignKey(Dataset, related_name='records')

    key = models.SlugField(max_length=255, blank=True, null=True)
    data = hstore.DictionaryField()

    label = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField()


class Field(models.Model):
    """
    A named field available within a dataset.

    `name`: the display name for the field
    `label`: the field used to label the data in a resulting Schema
    """
    namespace = models.ForeignKey(Namespace, related_name='fields')

    raw_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, null=True)


class Data(models.Model):
    """
    Stores a typed field/value pair for a given key within a namespace.
    """
    revisions = RevisionManager()
    revision = models.ForeignKey(Revision, related_name='dataset')
    version = models.CharField(max_length=255)

    key = models.SlugField()
    label = models.CharField(max_length=255)
    value = jsonfield.JSONField()
    facets = hstore.DictionaryField(blank=True, null=True)
    primary = models.BooleanField(default=False)


class Code(models.Model):
    """
    The code used to transform data.
    """
    slug = models.SlugField(max_length=255, unique=True)
    body = models.TextField()


class Transformation(models.Model):
    """
    The entire transformation applied to the data, including the source
    records and a reference to the code that was used to modify them.

    `source_field`: the direct source of the target primary Data
    `code`: the code used to tranform Records into secondary Data
    """
    revisions = RevisionManager()
    revision = models.ForeignKey(Revision)

    data = models.OneToOneField(Data, related_name='transformation')
    records = models.ForeignKey(Record, related_name='transformations')
    source_field = models.CharField(max_length=255, blank=True, null=True)
    code = models.ForeignKey(Code, null=True)
