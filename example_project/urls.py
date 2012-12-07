from django.conf.urls import patterns, url, include

from hstore_schema.api import *
from hstore_schema.models import *


v1_api = API(name='v1')

v1_api.register(RootResource())
v1_api.register(BucketListResource())
dataset_list = ModelListResource(model=Dataset)
v1_api.register(dataset_list)
dataset_detail = ModelDetailResource(model=Dataset)
v1_api.register(dataset_detail)
v1_api.register(dataset_detail.fields)

urlpatterns = patterns('',
    url(r'^api/v1/', include(v1_api.urls)),
)
