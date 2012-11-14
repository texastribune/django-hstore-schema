from example_project.data import registry


library = registry.register('district-staff')


@library.key(namespace='district', keyspace='cdc')
def district_cdc_number(record):
    for key in ['6 DIGIT COUNTY DISTRICT NUMBER',
                '6 Digit County District Number',
                'DISTRICT NUMBER',
                'DISTRICT',
                ]:
        try:
            return record[key]
        except KeyError:
            pass

    raise KeyError
