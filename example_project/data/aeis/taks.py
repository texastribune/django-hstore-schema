bucket = Bucket.objects.get_or_create(slug='public-ed',
        defaults={'name': 'Public Education', 'short_name': 'Public Ed'})

source = Source.objects.get_or_create(slug="aeis",
        defaults={'name': 'Academic Excellence Indicator System',
                  'short_name': 'AEIS', 'attribution': 'TEA'})

campus_taks = Dataset(name='Campus TAKS', bucket=bucket, source=source)


@campus_taks.key(namespace='campus', keyspace='cdc')
def key(record):
    return record['current 9-digit cdc number']


def facet(record, field, value):
    facets = {}

    # Facet on grade level
    match = re.search(r'Grade (\d+)', key)
    if match:
        facets['grade'] = match.group(1)

    # Facet on ethnicity
    if 'Two or More Races' in key:
        facets['ethnicity'] = 'Two or More Races'
    elif 'African American' in key:
        facets['ethnicity'] = 'African American'
    elif 'Hispanic' in key:
        facets['ethnicity'] = 'Hispanic'
    elif 'Native American' in key:
        facets['ethnicity'] = 'Native American'
    elif 'Asian/Pac Islander' in key:
        facets['ethnicity'] = 'Asian/Pacific Islander'
    elif 'Pacific Islander' in key:
        facets['ethnicity'] = 'Pacific Islander'
    elif 'Asian' in key:
        facets['ethnicity'] = 'Asian'
    elif 'White' in key:
        facets['ethnicity'] = 'White'

    # Facet on demographic
    if 'LEP' in key:
        facets['demographic'] = 'Limited English Proficient'
    elif 'Econ Disadv' in key:
        facets['demographic'] = 'Economically Disavdantaged'

    # Facet on subject
    if 'Mathematics' in key:
        facets['subject'] = 'Math'
    if 'Science' in key:
        facets['subject'] = 'Science'
    elif 'Social Studies' in key:
        facets['subject'] = 'Social Studies'
    elif 'Reading/ELA' in key:
        facets['subject'] = 'Reading/ELA'
    elif 'Writing' in key:
        facets['subject'] = 'Writing'

    # Facet on gender
    if 'Male' in key:
        facets['gender'] = 'Male'
    elif 'Female' in key:
        facets['gender'] = 'Female'

    # Facet on language
    if 'Non-Spanish' in key:
        facets['language'] = 'Spanish'
    elif 'Spanish' in key:
        facets['language'] = 'Spanish'

    return facets


# TODO: Map/reduce Asian and Pacific Islander aggregate ethnicities
@campus_taks.data(label='District Key', pattern=r'.* Rate$', facet=facet)
def taks_passing_rate(record, field, value, facets):
    # Negative values are masked
    masked = False
    if value:
        if value.startswith('-'):
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
    }
