from django.db import models
from django_hstore import hstore


class Data(models.Model):
    """
    Stores data for a key, source, and version.

    Data can be primary, meaning it is stored in its raw form, or secondary,
    meaning that it has been created by mapping and reducing primary data.
    """
    key = models.TextField()
    source = models.TextField()
    version = models.TextField()
    data = hstore.DictionaryField()
    primary = models.BooleanField(default=True)


class MetaData(models.Model):
    """
    Stores metadata about sources like notes, URLs, and field descriptions.
    """
    source = models.TextField()
    version = models.TextField()
    metadata = hstore.DictionaryField()


class Mapping(models.Model):
    """
    Maps raw source and field names to new source and field names.

    The mapped fields will be used to views to the original data, where each
    mapped source represents a distinct view.
    """
    raw_source = models.TextField(null=True)
    raw_version = models.TextField(null=True)
    raw_field = models.TextField()

    mapped_source = models.TextField()
    mapped_version = models.TextField()
    mapped_field = models.TextField()


class Field(models.Model):
    source = models.TextField(primary_key=True)
    version = models.TextField()
    field = models.TextField()

    class Meta:
        managed = False
