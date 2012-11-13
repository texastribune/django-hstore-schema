import glob
import os

from optparse import make_option

from csvkit import CSVKitDictReader
from django.core.management.base import BaseCommand


def package(files):
    # TODO: dataset.raw = package(files)
    return None


def get_files(version_path):
    csv_pattern = os.path.join(version_path, '*.csv')
    return glob.glob(csv_pattern)


def preview_file(dataset, csv):
    with open(csv) as f:
        reader = CSVKitDictReader(f)
        for data in reader:
            print str(data)[:77] + '...'


def load_file(dataset, f):
    pass


class Command(BaseCommand):
    """
    Loads and revises tabular data from disk.

    Expects the following folder structure:

    <source>/
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
        make_option('--dataset', action='store', dest='dataset'),
        make_option('--versions', action='store', dest='version'),
    )

    def handle(self, root, dataset=None, preview=False, **options):
        root = os.path.abspath(root)
        version_pattern = os.path.join(root, 'csv', '*')
        for version_path in glob.glob(version_pattern):
            version = os.path.basename(version_path)
            dataset = None

            # If version_path is a directory, load all CSVs inside it;
            # if it is a CSV, load it directly.
            if os.path.isdir(version_path):
                files = get_files(version_path)
            elif version_path.lower().endswith('.csv'):
                files = [version_path]

            if preview:
                for csv in files:
                    preview_file(dataset, csv)
