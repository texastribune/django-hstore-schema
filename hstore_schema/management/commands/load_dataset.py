from optparse import make_option
import glob
import os
import sys

from csvkit import CSVKitDictReader
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from hstore_schema.models import Bucket, Source, Dataset, Record
from hstore_schema.registry import registries


def package(files):
    # TODO: dataset.raw = package(files)
    return None


def get_files(version_path):
    csv_pattern = os.path.join(version_path, '*.csv')
    return glob.glob(csv_pattern)


def preview_file(dataset, register, csv):
    with open(csv) as f:
        base_name = os.path.basename(csv)
        label, ext = os.path.splitext(base_name)
        reader = CSVKitDictReader(f)
        for data in reader:
            record = Record(dataset=dataset, data=data, label=label,
                            order=reader.line_num)
            register.process(record)


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
        make_option('--versions', action='store', dest='versions',
                help='A comma-separated list of versions to load.'),
    )

    def handle(self, csv_dir, bucket_slug, dataset_slug=None, source_slug=None,
               versions=None, preview=False, **options):
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
        if versions is not None:
            versions = versions.split(',')

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
                version, ext = os.path.splitext(version_path)

            if preview:
                for csv in files:
                    dataset = Dataset(version=version)
                    preview_file(dataset, register, csv)
            else:
                dataset = Dataset.revisions.create_or_revise(
                    bucket=bucket, slug=dataset_slug, version=version,
                    defaults={'source': source})
                for csv in files:
                    if options['verbosity'] == '2':
                        print 'loading "%s"...' % csv
                    dataset.load_csv(csv)

        # TODO: Revise data associated with datasets
