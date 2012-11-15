from django.test import TestCase

from hstore_schema.models import Bucket, Source, Revision, Dataset, Record


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

    def test_record_headers(self):
        fields = ['Field 1', 'Field 2']
        values = ['1.0', '2.0']
        data_by_field = dict(zip(fields, values))
        dataset = Dataset(fields=fields)
        record = Record(
            dataset=dataset,
            data=dict([(i, data_by_field[f])
                       for i, f in enumerate(fields)]))
        self.assertEqual(record.data, {0: '1.0', 1: '2.0'})
        self.assertEqual(record.data_by_field, data_by_field)
