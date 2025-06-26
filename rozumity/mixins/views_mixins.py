from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema, OpenApiParameter
from adrf.viewsets import GenericViewSet
from adrf.generics import aget_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rozumity.mixins.caching_mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    UpdateModelMixin, DestroyModelMixin, Owned
)
from rozumity.mixins.serialization_mixins import AsyncSerializerMixin


class AsyncModelViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    authentication_classes = [JWTAuthentication]

    def __new__(cls, *args, **kwargs):
        self = GenericViewSet.__new__(cls)

        descriptions = getattr(cls, 'descriptions', {})

        def generate_schema_decorators(descriptions: dict):
            return {
                'alist': extend_schema(
                    description=descriptions.get('list', ''),
                    parameters=[
                        OpenApiParameter(name='offset', required=False, type=int),
                        OpenApiParameter(name='limit', required=False, type=int),
                    ]
                ),
                'aretrieve': extend_schema(description=descriptions.get('retrieve', '')),
                'acreate': extend_schema(description=descriptions.get('create', '')),
                'aupdate': extend_schema(description=descriptions.get('update', '')),
                'partial_aupdate': extend_schema(description=descriptions.get('partial_update', '')),
                'adestroy': extend_schema(description=descriptions.get('destroy', '')),
            }

        decorators = generate_schema_decorators(descriptions)

        for method_name, decorator in decorators.items():
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                if not getattr(method, '__spectacular__', False):
                    setattr(cls, method_name, decorator(method))
        if self.serializer_class:
            self.serializer_class.ato_representation = AsyncSerializerMixin.ato_representation
            self.serializer_class.arun_validation = AsyncSerializerMixin.arun_validation
            self.serializer_class.ais_valid = AsyncSerializerMixin.ais_valid
        return self

    async def aget_object(self):
        queryset = self.filter_queryset(await self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = await aget_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    async def get_queryset(self):
        return await sync_to_async(GenericViewSet.get_queryset)(self)


class AsyncReadOnlyModelViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    authentication_classes = [JWTAuthentication]

    def __new__(cls, *args, **kwargs):
        return AsyncModelViewSet.__new__(cls, *args, **kwargs)

    async def aget_object(self):
        return await AsyncModelViewSet.aget_object(self)

    async def aget_object(self):
        return await AsyncModelViewSet.aget_object(self)

    async def get_queryset(self):
        return await AsyncModelViewSet.get_queryset(self)
