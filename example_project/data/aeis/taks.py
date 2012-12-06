import re

from example_project.data import registry

campus_taks = registry.register('campus-taks')


@campus_taks.key(namespace='campus', keyspace='cdc')
def campus_cdc_key(record):
    for key in ['current 9-digit cdc number',
                'Campus Number',
                ]:
        try:
            return record.data[key]
        except KeyError:
            pass

    raise KeyError


@campus_taks.facet()
def facet(record, field, value):
    facets = {}

    # Facet on grade level
    match = re.search(r'Grade (\d+)', field)
    if match:
        facets['grade'] = match.group(1)

    # Facet on ethnicity
    if 'Two or More Races' in field:
        facets['ethnicity'] = 'Two or More Races'
    elif 'African American' in field:
        facets['ethnicity'] = 'African American'
    elif 'Hispanic' in field:
        facets['ethnicity'] = 'Hispanic'
    elif 'Native American' in field:
        facets['ethnicity'] = 'Native American'
    elif 'Asian/Pac Islander' in field:
        facets['ethnicity'] = 'Asian/Pacific Islander'
    elif 'Pacific Islander' in field:
        facets['ethnicity'] = 'Pacific Islander'
    elif 'Asian' in field:
        facets['ethnicity'] = 'Asian'
    elif 'White' in field:
        facets['ethnicity'] = 'White'

    # Facet on demographic
    if 'LEP' in field:
        facets['demographic'] = 'Limited English Proficient'
    elif 'Econ Disadv' in field:
        facets['demographic'] = 'Economically Disavdantaged'

    # Facet on subject
    if 'Mathematics' in field:
        facets['subject'] = 'Math'
    if 'Science' in field:
        facets['subject'] = 'Science'
    elif 'Social Studies' in field:
        facets['subject'] = 'Social Studies'
    elif 'Reading/ELA' in field:
        facets['subject'] = 'Reading/ELA'
    elif 'Writing' in field:
        facets['subject'] = 'Writing'

    # Facet on gender
    if 'Male' in field:
        facets['gender'] = 'Male'
    elif 'Female' in field:
        facets['gender'] = 'Female'

    # Facet on language
    if 'Non-Spanish' in field:
        facets['language'] = 'Spanish'
    elif 'Spanish' in field:
        facets['language'] = 'Spanish'

    return facets


# TODO: Map/reduce Asian and Pacific Islander aggregate ethnicities
@campus_taks.field_data(namespace='campus', label='District Key',
                        pattern=r'.* Rate$')
def taks_passing_rate(record, field, value, facets=None):
    # Negative values are masked
    masked = False
    if value:
        if value.startswith('-') or value == '.':
            value = None
            masked = True
        else:
            value = float(value)
    else:
        value = None

    return {
        'key': record.key,
        'value': value,
        'masked': masked,
        'version': record.dataset.version,
        'facets': facets,
    }
