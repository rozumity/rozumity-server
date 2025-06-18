from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rozumity.mixins.caching_mixins import *
from rozumity.mixins.schema_mixins import *

from rozumity.permissions import *
from rozumity.mixins.filtering_mixins import Owned
from screening.permissions import *

from screening.models import *
from screening.serializers import *


class TagScreeningReadOnlyViewSet(ReadOnlyModelViewSet, SchemaMixin):
    queryset = TagScreening.objects.all()
    serializer_class = TagScreeningSerializer
    permission_classes = (IsUser,)
    descriptions = {
        'list': 'API view to retrieve a list of all tags.',
        'retrieve': 'API view to retrieve a single tag by its ID.'
    }


class QuestionaryCategoryReadOnlyViewSet(ReadOnlyModelViewSet, SchemaMixin):
    queryset = QuestionaryCategory.objects.all()
    serializer_class = QuestionaryCategorySerializer
    permission_classes = (IsUser,)
    descriptions = {
        'list': 'API view to retrieve a list of all questionary categories.',
        'retrieve': 'API view to retrieve a single questionary category by its ID.'
    }


class QuestionaryReadOnlyViewSet(ReadOnlyModelViewSet, SchemaMixin):
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
            qs = qs.filter(categories__in=categories)
        if tags:
            qs = qs.filter(tags__in=tags)
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
        return await super().alist(request, *args, **kwargs)


class QuestionaryAnswerReadOnlyViewSet(Owned, ReadOnlyModelViewSet, SchemaMixin):
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)
    descriptions = {'list': 'API view to retrieve a list of all possible answers for questionary questions.'}


class QuestionaryResponseViewSet(Owned, CachedModelViewSet, SchemaMixin):
    queryset = QuestionaryResponse.objects.all()
    permission_classes = (IsResponsePublic,)
    descriptions = {
        'list': 'API view to list questionary responses.\nUses ownership filtering.',
        'create': 'API view to create questionary responses.',
        'retrieve': 'API view to retrieve a single questionary response by its ID.\nUses ownership access.',
        'update': 'API view to update a single questionary response by its ID.\nUses ownership access.',
        'partial_update': 'API view to partial update a single questionary response by its ID.\nUses ownership access.'
    }

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return QuestionaryResponseReadOnlySerializer
        return QuestionaryResponseSerializer

    async def acreate(self, request, *args, **kwargs):
        request.data['client'] = str(request.user.id)
        return await CachedModelViewSet.acreate(self, request, *args, **kwargs)
