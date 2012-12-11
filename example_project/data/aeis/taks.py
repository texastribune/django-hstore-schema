import re

from example_project.data import registry

campus_taks = registry.register('campus-taks')
campus_taks_commended = registry.register('campus-taks-commended')
campus_taks_met_standard = registry.register('campus-taks-met-standard')


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


@campus_taks.facet('grade', required=True)
def facet_grade(record, field, value):
    match = re.search(r'Grade (\d+)', field)
    if match:
        return match.group(1)


@campus_taks.facet('ethnicity')
@campus_taks_commended.facet('ethnicity')
@campus_taks_met_standard.facet('ethnicity')
def facet_ethnicity(record, field, value):
    if 'Two or More Races' in field:
        return 'Two or More Races'
    elif 'African American' in field:
        return 'African American'
    elif 'Hispanic' in field:
        return 'Hispanic'
    elif 'Native American' in field:
        return 'Native American'
    elif 'Asian/Pac Islander' in field:
        return 'Asian/Pacific Islander'
    elif 'Pacific Islander' in field:
        return 'Pacific Islander'
    elif 'Asian' in field:
        return 'Asian'
    elif 'White' in field:
        return 'White'


@campus_taks.facet('demographic')
@campus_taks_commended.facet('demographic')
@campus_taks_met_standard.facet('demographic')
def facet_demographic(record, field, value):
    if 'LEP' in field:
        return 'Limited English Proficient'
    elif 'Econ Disadv' in field:
        return 'Economically Disavdantaged'


@campus_taks.facet('subject')
@campus_taks_commended.facet('subject')
@campus_taks_met_standard.facet('subject')
def facet_subject(record, field, value):
    if 'Mathematics' in field:
         return 'Math'
    if 'Science' in field:
         return 'Science'
    elif 'Social Studies' in field:
         return 'Social Studies'
    elif 'Reading/ELA' in field:
         return 'Reading/ELA'
    elif 'Writing' in field:
         return 'Writing'


@campus_taks.facet('gender')
@campus_taks_commended.facet('gender')
@campus_taks_met_standard.facet('gender')
def facet_gender(record, field, value):
    if 'Male' in field:
        return 'Male'
    elif 'Female' in field:
        return 'Female'


@campus_taks.facet('language')
def facet_language(record, field, value):
    if 'Non-Spanish' in field:
        return 'Spanish'
    elif 'Spanish' in field:
        return 'Spanish'


# TODO: Map/reduce Asian and Pacific Islander aggregate ethnicities
@campus_taks.field_data('passing_rate', label='Passing Rate',
        namespace='campus', pattern=r'.* Rate$')
@campus_taks_commended.field_data('commended_rate', label='Commended Rate',
        namespace='campus', pattern=r'.* Rate$')
@campus_taks_met_standard.field_data('passing_rate', label='Passing Rate',
        namespace='campus', pattern=r'.* Rate$')
def get_taks_value(record, field, value, facets=None):
    masked = False
    if value:
        # Negative values are masked
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
