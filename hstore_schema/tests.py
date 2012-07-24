from django.test import TestCase

from .models import Data


class TestModels(TestCase):
    def test_data(self):
        data = Data()
        self.assertEqual(data.source, '')
        self.assertEqual(data.version, '')
        self.assertEqual(data.data, {})
