from django.core.urlresolvers import reverse
from django.test import TestCase

from hstore_schema.models import Bucket, Source, Revision, Dataset


class TestModels(TestCase):
    def setUp(self):
        self.bucket = Bucket.objects.create(
            name='Public Education', short_name='Public Ed', slug='public-ed')
        self.source = Source.objects.create(
            name='AEIS', short_name='AEIS', slug='aeis')

    def test_revision(self):
        r = Revision()
        self.assertTrue(not r.digest)
        r.save()
        self.assertTrue(r.digest is not None)
        self.assertTrue(r.time is not None)

    def test_current(self):
        old_revision = Revision.objects.create()
        old_dataset = Dataset.objects.create(
            bucket=self.bucket, source=self.source,
            name='Test', slug='test', version='old', revision=old_revision)
        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(Dataset.revisions.current().count(), 1)
        self.assertEqual(Dataset.revisions.current().all()[0], old_dataset)
        new_revision = Revision.objects.create(previous=old_revision)
        new_dataset = Dataset.objects.create(
            bucket=self.bucket, source=self.source,
            name='Test', slug='test', version='new', revision=new_revision)
        self.assertEqual(Dataset.objects.count(), 2)
        self.assertEqual(Dataset.revisions.current().count(), 1)
        self.assertEqual(Dataset.revisions.current().all()[0], new_dataset)

    def test_create_or_revise(self):
        self.assertEqual(Revision.objects.count(), 0)
        old_dataset = Dataset.revisions.create_or_revise(
            bucket=self.bucket, source=self.source, slug='test',
            defaults={'name': 'Test', 'version': '2012'})
        self.assertEqual(Revision.objects.count(), 1)
        self.assertEqual(old_dataset.revision, Revision.objects.all()[0])
        new_dataset = Dataset.revisions.create_or_revise(
            bucket=self.bucket, source=self.source,
            slug='test', version='2012', defaults={'name': 'Test'})
        self.assertEqual(Revision.objects.count(), 2)
        self.assertEqual(new_dataset.revision.previous, old_dataset.revision)

    def test_api(self):
        url = reverse('dataset_list', kwargs={'api_version': 1})
