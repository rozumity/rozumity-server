from drf_spectacular.utils import extend_schema, OpenApiParameter
from adrf.viewsets import GenericViewSet
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

        self.serializer_class.ato_representation = AsyncSerializerMixin.ato_representation
        self.serializer_class.arun_validation = AsyncSerializerMixin.arun_validation
        self.serializer_class.ais_valid = AsyncSerializerMixin.ais_valid
        return self


class AsyncReadOnlyModelViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    def __new__(cls, *args, **kwargs):
        return AsyncModelViewSet.__new__(cls, *args, **kwargs)
