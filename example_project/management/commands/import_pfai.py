from example_project.utils import import_pfai_file

from django.core.management.base import BaseCommand
from hstore_schema.models import Data


class Command(BaseCommand):
    def handle(self, path, **options):
        import_pfai_file(path)
