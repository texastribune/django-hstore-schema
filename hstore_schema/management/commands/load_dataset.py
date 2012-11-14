from optparse import make_option
import glob
import os

from csvkit import CSVKitDictReader
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from hstore_schema.models import Bucket, Source, Dataset
from hstore_schema.registry import registries


def package(files):
    # TODO: dataset.raw = package(files)
    return None


def get_files(version_path):
    csv_pattern = os.path.join(version_path, '*.csv')
    return glob.glob(csv_pattern)


def preview_file(register, csv):
    with open(csv) as f:
        reader = CSVKitDictReader(f)
        for row in reader:
            print str(row)[:77] + '...'
            try:
                key = register._key(row)
            except KeyError:
                key = None
                import pprint
                pprint.pprint(row)
                exit()
            print '->', repr(key)


def load_file(dataset, csv):
    pass


class Command(BaseCommand):
    """
    Loads a Dataset from tabular data from disk.

    Expects the following folder structure:

    <source1>
    <source2>
        <dataset1>/
            csv/
                <version_01>/
                    <version_01a>.csv
                    <version_01b>.csv
                <version_02>/
                <version_03>.csv
                ...
    """

    help = 'Revise data using new source data and code'
    option_list = BaseCommand.option_list + (
        make_option('--preview', action='store_true', dest='preview',
            help='Print keys and values that will be generated without '
                 'actually saving the revised data'),
        make_option('--bucket', action='store', dest='bucket_slug'),
        make_option('--dataset', action='store', dest='dataset_slug'),
        make_option('--source', action='store', dest='source_slug'),
        make_option('--versions', action='store', dest='versions'),
    )

    def handle(self, csv_dir, bucket_slug, dataset_slug=None, source_slug=None,
               versions=None, **options):
        csv_dir = os.path.abspath(csv_dir)
        dataset_dir = os.path.dirname(csv_dir)
        source_dir = os.path.dirname(dataset_dir)

        # Get dataset name from parent directory
        if not dataset_slug:
            dataset_slug = os.path.basename(dataset_dir)
            dataset_slug = slugify(dataset_slug).replace('_', '-')

        # Get source name from grandparent directory
        if source_slug is None:
            source_slug = os.path.basename(source_dir)
            source_slug = slugify(source_slug).replace('_', '-')

        # Get or create bucket
        bucket, created = Bucket.objects.get_or_create(slug=bucket_slug,
                defaults={'name': bucket_slug, 'short_name': bucket_slug})

        # Get or create source
        source, created = Source.objects.get_or_create(slug=source_slug,
                defaults={'name': source_slug, 'short_name': source_slug})

        # Get register for the dataset
        registry = registries.get(bucket.slug, {})
        register = registry.get(dataset_slug)

        # Limit versions
        if 'versions' in options:
            versions = options['versions'].split(',')
        else:
            versions = None

        # Load specified versions of the data
        version_pattern = os.path.join(csv_dir, '*')
        for version_path in glob.glob(version_pattern):
            version = os.path.basename(version_path)
            if versions and version not in versions:
                continue

            # If version_path is a directory, load all CSVs inside it;
            # if it is a CSV, load it directly.
            if os.path.isdir(version_path):
                files = get_files(version_path)
            elif version_path.lower().endswith('.csv'):
                files = [version_path]

            if 'preview' in options:
                for csv in files:
                    preview_file(register, csv)
            else:
                dataset = Dataset.revisions.create_or_revise(
                    bucket=bucket, slug=dataset, version=version,
                    defaults={'source': source})
                for csv in files:
                    load_file(dataset, csv)

        # TODO: Revise data associated with datasets
