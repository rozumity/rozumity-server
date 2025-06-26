from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rozumity.mixins.views_mixins import (
    AsyncModelViewSet, AsyncReadOnlyModelViewSet, Owned
)

from rozumity.permissions import *
from screening.permissions import *
from screening.models import *
from screening.serializers import *


class TagScreeningReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    queryset = TagScreening.objects.all()
    serializer_class = TagScreeningSerializer
    permission_classes = (IsUser,)
    descriptions = {
        'list': 'API view to retrieve a list of all tags.',
        'retrieve': 'API view to retrieve a single tag by its ID.'
    }


class CategoryScreeningReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    queryset = CategoryScreening.objects.all()
    serializer_class = CategoryScreeningSerializer
    permission_classes = (IsUser,)
    descriptions = {
        'list': 'API view to retrieve a list of all questionary categories.',
        'retrieve': 'API view to retrieve a single questionary category by its ID.'
    }


class QuestionaryReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)
    descriptions = {
        'list': 'API view to retrieve a list of all questionaries.',
        'retrieve': 'API view to retrieve a single questionary by its ID.'
    }

    def get_queryset(self):
        qs = Questionary.objects.all()
        categories = self.request.query_params.getlist("categories")
        tags = self.request.query_params.getlist("tags")
        if categories:
            qs = qs.filter(questionary_to_category__category__in=categories)
        if tags:
            qs = qs.filter(questionary_to_tag__tag__in=tags)
        return qs.distinct()
    
    @extend_schema(parameters=[
        OpenApiParameter(
            name='categories', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
            description='Filter by categories (can be repeated)',  style='form', explode=True,
        ),
        OpenApiParameter(
            name='tags', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, 
            description='Filter by tags (can be repeated)', style='form', explode=True,
        ),
    ])
    async def alist(self, request, *args, **kwargs):
        return await AsyncReadOnlyModelViewSet.alist(self, request, *args, **kwargs)


class QuestionaryAnswerReadOnlyViewSet(Owned, AsyncReadOnlyModelViewSet):
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)
    descriptions = {'list': 'API view to retrieve a list of all possible answers for questionary questions.'}


class QuestionaryResponseViewSet(Owned, AsyncModelViewSet):
    queryset = QuestionaryResponse.objects.all()
    permission_classes = (IsResponsePublic,)
    serializer_class = QuestionaryResponseSerializer
    descriptions = {
        'list': 'API view to list questionary responses.\nUses ownership filtering.',
        'create': 'API view to create questionary responses.',
        'retrieve': 'API view to retrieve a single questionary response by its ID.\nUses ownership access.',
        'update': 'API view to update a single questionary response by its ID.\nUses ownership access.',
        'partial_update': 'API view to partial update a single questionary response by its ID.\nUses ownership access.'
    }

    @extend_schema(parameters=[
        OpenApiParameter(
            name='questionary', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
            description='Filter by questionaries',  style='form', explode=True
        ),
        OpenApiParameter(
            name='is_filled', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY,
            description='Filter filled responses',  style='form'
        ),
        OpenApiParameter(
            name='is_checked', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY,
            description='Filter checked responses with results',  style='form'
        ),
    ])
    async def alist(self, request, *args, **kwargs):
        return await AsyncModelViewSet.alist(self, request, *args, **kwargs)

    async def acreate(self, request, *args, **kwargs):
        request.data['client'] = str(request.user.id)
        return await AsyncModelViewSet.acreate(self, request, *args, **kwargs)

    def get_queryset(self):
        qs = self.queryset
        questionary_id = self.request.query_params.get("questionary")
        is_filled = self.request.query_params.get("is_filled", None)
        is_checked = self.request.query_params.get("is_checked", None)
        if questionary_id:
            qs = qs.filter(questionary_id=int(questionary_id))
        if is_filled is not None:
            qs = qs.filter(is_filled=is_filled == 'true')
        if is_checked is not None:
            qs = qs.filter(is_checked=is_checked == 'true')
        return qs.distinct()
