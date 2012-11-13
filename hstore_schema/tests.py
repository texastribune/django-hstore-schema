from django.test import TestCase


class TestModels(TestCase):
    def test_revision(self):
        r = Revision()
        self.assertEqual(r.digest, None)
        r.save()
        self.assertTrue(r.digest is not None)
        self.assertTrue(r.time is not None)

    def test_current(self):
        old_revision = Revision.objects.create()
        old_dataset = Dataset.objects.create(
            name='Test', slug='test', version='old', revision=old_revision)
        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(Dataset.current.count(), 1)
        self.assertEqual(Dataset.current.all()[0], old_dataset)
        new_revision = Revision.objects.create(previous=old_revision)
        new_dataset = Dataset.objects.create(
            name='Test', slug='test', version='new', revision=old_revision)
        self.assertEqual(Dataset.objects.count(), 2)
        self.assertEqual(Dataset.current.count(), 1)
        self.assertEqual(Dataset.current.all()[0], new_dataset)
