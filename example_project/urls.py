from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()


# API URLs
from hstore_schema.api import *

urlpatterns +=patterns('',
    url(r'^api/buckets/$',
            BucketListResource.as_view(),
            name='bucket_list_resource'),
    url(r'^api/datasets/(?P<bucket_slug>[\w\-\_]+)/$',
            DatasetListResource.as_view(),
            name='bucket_list_resource'),
    url(r'^api/records/(?P<bucket_slug>[\w\-\_]+)/' + \
        r'(?P<dataset_slug>[\w\-\_]+)/(?P<version>[\w\-\_]+)/$',
            RecordListResource.as_view(),
            name='dataset_list_resource'),
    url(r'^api/fields/(?P<bucket_slug>[\w\-\_]+)/' + \
        r'(?P<dataset_slug>[\w\-\_]+)/(?P<version>[\w\-\_]+)/$',
            DatasetFieldListResource.as_view(),
            name='dataset_field_list_resource'),
)
