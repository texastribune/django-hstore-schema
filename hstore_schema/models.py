import os
import uuid

from csvkit import CSVKitDictReader
from django.db import models
from django_hstore import hstore
import jsonfield

from hstore_schema.registry import registries


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
    previous = models.OneToOneField('self', null=True, related_name='next')
    # TODO: Add a timestamp field
    # This will allow a `by_time` method on the RevisionManager that
    # returns data current for a specific point in time by querying
    # (revision__timestamp__lte=<time>, revision__next__timestamp__gt=<time>)

    def save(self, *args, **kwargs):
        if not self.digest:
            self.digest = uuid.uuid4().hex

        super(Revision, self).save(*args, **kwargs)

    @property
    def time(self):
        return uuid.UUID(self.digest).time


class RevisionManager(models.Manager):
    def current(self):
        return self.get_query_set().filter(revision__next__isnull=True)

    def create_or_revise(self, **kwargs):
        """
        Works like `get_or_create` but always creates a new revision.
        """
        defaults = kwargs.pop('defaults', None)

        try:
            old = self.current().select_related('revision').get(**kwargs)
            revision = Revision.objects.create(previous=old.revision)
        except self.model.DoesNotExist:
            revision = Revision.objects.create()

        if defaults:
            kwargs.update(**defaults)
        return self.create(revision=revision, **kwargs)


class Dataset(models.Model):
    """
    A named set of data that is sourced from raw files.
    """
    bucket = models.ForeignKey(Bucket, related_name='datasets')

    objects = models.Manager()
    revisions = RevisionManager()

    revision = models.ForeignKey(Revision, related_name='datasets')
    version = models.CharField(max_length=255)

    source = models.ForeignKey(Source, related_name='datasets')

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    raw = models.FileField(upload_to='datasets', blank=True, null=True)

    class Meta:
        unique_together = ('bucket', 'revision', 'slug', 'version')
        ordering = ('bucket', 'slug', 'version')

    def load_csv(self, csv, batch_size=1000):
        records = []
        with open(csv) as f:
            base_name = os.path.basename(csv)
            label, ext = os.path.splitext(base_name)
            reader = CSVKitDictReader(f)

            # Save field names
            for order, name in enumerate(reader.fieldnames):
                Field.objects.create(dataset=self, label=label, order=order,
                                     name=name)

            # Read records and save in batches
            for data in reader:
                record = Record(dataset=self, data=data, label=label,
                                order=reader.line_num)
                records.append(record)
                if len(records) >= batch_size:
                    Record.objects.bulk_create(records)
                    records = []

            # Save any remaining records
            if records:
                Record.objects.bulk_create(records)


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

    class Meta:
        ordering = ('dataset', 'label', 'order')

    @property
    def _register(self):
        registry = registries.get(self.dataset.bucket.slug)
        return registry.get(self.dataset.slug)

    @property
    def _data(self):
        data = []
        if self._register and self._register._field_data:
            for field, f in self._register._field_data.iteritems():
                for d in f(self):
                    if d:
                        d['field'] = field
                        data.append(d)

        return data

    @property
    def _key(self):
        if self._register and self._register._key:
            return self._register._key(self)

        return None


class Field(models.Model):
    """
    A named field available within a dataset.

    `name`: the display name for the field
    `label`: the field used to label the data in a resulting Schema
    """
    dataset = models.ForeignKey(Dataset, related_name='fields')
    label = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('dataset', 'label', 'order')


class Data(models.Model):
    """
    Stores a typed field/value pair for a given key within a namespace.
    """
    objects = models.Manager()
    revisions = RevisionManager()

    revision = models.ForeignKey(Revision, related_name='dataset')
    version = models.CharField(max_length=255)

    key = models.SlugField()
    slug = models.SlugField()
    label = models.CharField(max_length=255)
    value = jsonfield.JSONField()
    facets = hstore.DictionaryField(blank=True, null=True)
    primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('revision', 'key', 'slug', 'facets')


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
    objects = models.Manager()
    revisions = RevisionManager()

    revision = models.ForeignKey(Revision)

    data = models.OneToOneField(Data, related_name='transformation')
    records = models.ForeignKey(Record, related_name='transformations')
    source_field = models.CharField(max_length=255, blank=True, null=True)
    code = models.ForeignKey(Code, null=True)
