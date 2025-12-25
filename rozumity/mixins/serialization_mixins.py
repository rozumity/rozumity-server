from asgiref.sync import sync_to_async
from django_countries.serializers import CountryFieldMixin


class CountryFieldMixinAsync(CountryFieldMixin):
    async def build_standard_field(self, field_name, model_field):
        return sync_to_async(super().build_standard_field)(field_name, model_field)


class ReadOnlySerializerMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.read_only = True
