from adrf.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rozumity.mixins.caching_mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    UpdateModelMixin, DestroyModelMixin, Owned
)


class AsyncModelViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    authentication_classes = [JWTAuthentication]


class AsyncReadOnlyModelViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    authentication_classes = [JWTAuthentication]