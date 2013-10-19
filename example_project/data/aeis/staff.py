from example_project.data import registry

district_staff = registry.register('district-staff')


@district_staff.key(namespace='district', keyspace='cdc')
def district_cdc_number(record):
    for key in ['current district co_dist number',
                '6 DIGIT COUNTY DISTRICT NUMBER',
                '6 Digit County District Number',
                'DISTRICT NUMBER',
                'DISTRICT',
                ]:
        try:
            return record.data[key]
        except KeyError:
            pass

    raise KeyError
