from django.db import models
from django.template.defaultfilters import slugify
from django_hstore import hstore


class Source(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Source, self).save(**kwargs)


class Data(models.Model):
    """
    Stores data for a key, source, and version.

    Data can be primary, meaning it is stored in its raw form, or secondary,
    meaning that it has been created by mapping and reducing primary data.
    """
    key = models.TextField()
    source = models.ForeignKey(Source, related_name='data')
    version = models.SlugField()
    data = hstore.DictionaryField()
    primary = models.BooleanField(default=True)


class MetaData(models.Model):
    """
    Stores metadata about sources like notes, URLs, and field descriptions.
    """
    source = models.ForeignKey(Source, related_name='metadata')
    version = models.SlugField()
    metadata = hstore.DictionaryField()

    class Meta:
        unique_together = ('source', 'version')


class Mapping(models.Model):
    """
    Maps version and field names from a Source to new version and field names.

    The mapped fields will be used to views to the original data, where each
    mapped source represents a distinct view.
    """
    source = models.ForeignKey(Source, related_name='mappings')

    source_version = models.SlugField(null=True)
    source_field = models.TextField()

    mapped_version = models.SlugField()
    mapped_field = models.TextField()


class Field(models.Model):
    source = models.ForeignKey(Source, related_name='fields')
    version = models.SlugField()
    field = models.TextField()

    class Meta:
        managed = False
