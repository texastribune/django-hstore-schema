from django.conf.urls import patterns, url, include

from hstore_schema.api import *
from hstore_schema.models import *


v1_api = API(name='v1')

v1_api.register(RootResource())
v1_api.register(ModelListResource(model=Bucket))
v1_api.register(ModelListResource(model=Dataset))
v1_api.register(ModelListResource(model=Record))
v1_api.register(ModelListResource(model=Field))

urlpatterns = patterns('',
    url(r'^api/v1/', include(v1_api.urls)),
)
