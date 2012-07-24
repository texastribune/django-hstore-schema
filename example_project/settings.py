import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__)))
STATICFILES_DIRS = (os.path.join(PROJECT_PATH, 'static'),)
STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
                       "django.contrib.staticfiles.finders.AppDirectoriesFinder")
STATIC_URL = '/static/'
SECRET_KEY = 'k^+o!9jb-6hc*9dlrm$x!#2^zpond1u9=sob4p4(s-@v8(0(q('
TEMPLATE_LOADERS = ('django.template.loaders.app_directories.Loader',
                    'django.template.loaders.filesystem.Loader',)
MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',)
ROOT_URLCONF = 'example_project.urls'
TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates'),)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'example_project',
    'hstore_schema',
)

from local_settings import *
