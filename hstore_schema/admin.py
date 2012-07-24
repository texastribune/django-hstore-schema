from django.contrib import admin

from hstore_schema.models import Data, MetaData, Mapping

admin.site.register(Data)
admin.site.register(MetaData)
admin.site.register(Mapping)
