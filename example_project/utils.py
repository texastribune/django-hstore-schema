import codecs
import os.path

from csvkit import CSVKitDictReader
from hstore_schema.models import Source, Data


def import_pfai_file(path):
    filename = os.path.basename(path)
    basename, ext = os.path.splitext(filename)
    version = basename.split('_')[-1]  # Year

    source, created = Source.objects.get_or_create(name='Raw PFAI')
    version_data = dict(source=source, version=version)
    Data.objects.filter(**version_data).delete()
    with codecs.open(path, encoding='iso-8859-1') as f:
        reader = CSVKitDictReader(f)
        for row in reader:
            numeric_key = int(float(row['District ID']))
            key = str(numeric_key).zfill(6)
            Data.objects.create(key=key, data=row, **version_data)
