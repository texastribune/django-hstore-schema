from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from hstore_schema.api import (BucketList, BucketDetail, DatasetList,
        DatasetDetail, RecordList, RevisionDetail, FieldList)


urlpatterns = patterns('hstore_schema.api',
    url(r'^$', 'api_root'),
    url(r'^buckets/$',
        BucketList.as_view(),
        name='bucket_list'),
    url(r'^bucket/(?P<pk>[\w\-\_]+)/$',
        BucketDetail.as_view(),
        name='bucket_detail'),
    url(r'^datasets/$',
        DatasetList.as_view(),
        name='dataset_list'),
    url(r'^datasets/(?P<pk>\d+)/$',
        DatasetDetail.as_view(),
        'dataset_detail'),
    url(r'^records/$',
        RecordList.as_view(),
        name='record_list'),
    url(r'^revisions/(?P<pk>\d+)/$',
        RevisionDetail.as_view(),
        name='revision_detail'),
    url(r'^fields/$',
        FieldList.as_view(),
        name='field_list')
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
