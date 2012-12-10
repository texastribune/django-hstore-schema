from django.conf.urls import patterns, url, include

from hstore_schema.api import *
from hstore_schema.models import *


v1_api = API(name='v1')

root = RootResource()
bucket_list = ModelListResource(model=Bucket)
record_list = ModelListResource(model=Record)
field_list = ModelListResource(model=Field)
dataset_list = DatasetListResource()
dataset_detail = DatasetDetailResource()

v1_api.register(root)
v1_api.register(bucket_list)
v1_api.register(record_list)
v1_api.register(field_list)
v1_api.register(dataset_list)
v1_api.register(dataset_detail)
v1_api.register(dataset_detail.records)
v1_api.register(dataset_detail.fields)

urlpatterns = patterns('',
    url(r'^api/v1/', include(v1_api.urls)),
)
