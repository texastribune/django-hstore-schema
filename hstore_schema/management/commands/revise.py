from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Revises all data in the given bucket.
    """

    help = 'Revise data using new source data and code'
    option_list = BaseCommand.option_list + (
        make_option('--bucket', action='store', dest='dataset'),
        make_option('--namespace', action='store', dest='namespace'),
        make_option('--version', action='store', dest='version'),
    )

    def handle(self, bucket, namespace=None, version=None, **options):
        pass
