from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from adrf.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView,  CreateAPIView, RetrieveUpdateAPIView, GenericAPIView
from rozumity.mixins.caching_mixins import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rozumity.permissions import *
from rozumity.mixins.filtering_mixins import Owned
from screening.permissions import *

from screening.models import *
from screening.serializers import *


class TagScreeningReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all tags.
    API view to retrieve a single tag by its ID.
    """
    queryset = TagScreening.objects.all()
    serializer_class = TagScreeningSerializer
    permission_classes = (IsUser,)


class QuestionaryCategoryReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all questionary categories.
    API view to retrieve a single questionary category by its ID.
    """
    queryset = QuestionaryCategory.objects.all()
    serializer_class = QuestionaryCategorySerializer
    permission_classes = (IsUser,)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='categories', description='Filter by categories', required=False, type=int, many=True
            ),
            OpenApiParameter(
                name='tags', description='Filter by tags', required=False, type=int, many=True
            ),
        ]
    )
)
class QuestionaryReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all questionaries.
    API view to retrieve a single questionary by its ID.
    """
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = Questionary.objects.all()
        categories = self.request.query_params.getlist("categories")
        tags = self.request.query_params.getlist("tags")
        if categories:
            qs = qs.filter(categories__in=categories)
        if tags:
            qs = qs.filter(tags__in=tags)
        return qs.distinct()


class QuestionaryAnswerReadOnlyViewSet(Owned, ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all possible answers for questionary questions.
    """
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)


class QuestionaryResponseViewSet(Owned, CachedModelViewSet):
    """
    API view to list questionary responses.
    Uses ownership filtering.
    API view to retrieve a single questionary response by its ID.
    Uses ownership access.
    API view to create questionary responses.
    API view to update a single questionary response by its ID.
    Uses ownership access.
    """
    queryset = QuestionaryResponse.objects.all()
    permission_classes = (IsResponsePublic,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return QuestionaryResponseReadOnlySerializer
        return QuestionaryResponseSerializer

    async def acreate(self, request, *args, **kwargs):
        request.data['client'] = str(request.user.id)
        return await CachedModelViewSet.acreate(self, request, *args, **kwargs)
