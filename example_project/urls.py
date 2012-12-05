from django.conf.urls import patterns, url, include
from tastypie.api import Api

from hstore_schema.api import *


v1_api = Api(api_name='v1')

v1_api.register(RootResource())
v1_api.register(BucketResource())
v1_api.register(DatasetResource())

record_resource = RecordResource()
field_resource = FieldResource()
v1_api.register(record_resource)
v1_api.register(field_resource)

urlpatterns = patterns('',
    url(r'^api/v1/records/(?P<bucket_slug>\w[\w\-]+)/(?P<dataset_slug>\w[\w\-]+)/(?P<version>\w[\w\-]+)/',
        include(record_resource.urls)),
    url(r'^api/v1/fields/(?P<bucket_slug>\w[\w\-]+)/(?P<dataset_slug>\w[\w\-]+)/(?P<version>\w[\w\-]+)/',
        include(field_resource.urls)),
    url(r'^api/', include(v1_api.urls)),
)
