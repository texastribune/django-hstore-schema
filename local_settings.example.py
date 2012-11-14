HSTORE_TEMPLATE = 'template_postgis'
DATABASES = {
    'default': {
        'ENGINE': 'django_hstore.postgresql_psycopg2',
        'NAME': 'hstoreschema',
        'USER': 'hstoreschema',
        'OPTIONS': {'autocommit': True},
    },
}
