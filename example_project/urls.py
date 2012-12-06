from django.conf.urls import patterns, url, include
from tastypie.api import Api

from hstore_schema.api import *


v1_api = Api(api_name='v1')

v1_api.register(RootResource())
v1_api.register(BucketResource())
v1_api.register(DatasetResource())
v1_api.register(RecordResource())
v1_api.register(FieldResource())

urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
)
