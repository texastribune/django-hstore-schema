from hstore_schema.mapreduce import MapReduce
from hstore_schema.models import Data

mr = MapReduce()


@mr.map('RAW_PFAI')
def map_pfai_values(value, field, source, **kwargs):
    lower_field = field.lower()
    if (value and value.strip() != '< 5'
            and 'total' in lower_field and 'percent' not in lower_field
            and '%' not in lower_field):
        try:
            yield dict(value=float(value), field=field, source='CLEANED_PFAI',
                       **kwargs)
        except ValueError:
            pass


@mr.reduce('CLEANED_PFAI')
def reduce_pfai_values(data, values, field, **kwargs):
    data.data[field] = '%.2f' % sum(values)


if __name__ == '__main__':
    Data.objects.filter(source='CLEANED_PFAI').delete()
    mr.run()
