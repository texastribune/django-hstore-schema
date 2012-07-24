DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'tribdata',
        'USER': 'tribdata',
        'PASSWORD': 'trib101',
        'OPTIONS': {'autocommit': True},
    },
}
