import django_filters.rest_framework
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from adrf.generics import *
from rozumity.mixins.caching_mixins import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rozumity.permissions import *
from rozumity.mixins.filtering_mixins import OwnedList
from screening.permissions import *

from screening.models import *
from screening.serializers import *


class TagScreeningListView(ListMixin, ListAPIView):
    """
    API view to retrieve a list of all tags.
    """
    queryset = TagScreening.objects.all()
    serializer_class = TagScreeningSerializer
    permission_classes = (IsUser,)


class TagScreeningRetrieveView(RetrieveMixin, RetrieveAPIView):
    """
    API view to retrieve a single tag by its ID.
    """
    queryset = TagScreening.objects.all()
    serializer_class = TagScreeningSerializer
    permission_classes = (IsUser,)


class QuestionaryCategoryListView(ListMixin, ListAPIView):
    """
    API view to retrieve a list of all questionary categories.
    """
    queryset = QuestionaryCategory.objects.all()
    serializer_class = QuestionaryCategorySerializer
    permission_classes = (IsUser,)


class QuestionaryCategoryRetrieveView(RetrieveMixin, RetrieveAPIView):
    """
    API view to retrieve a single questionary category by its ID.
    """
    queryset = QuestionaryCategory.objects.all()
    serializer_class = QuestionaryCategorySerializer
    permission_classes = (IsUser,)


@extend_schema(parameters=[
    OpenApiParameter(
        name='categories', description='Filter by categories', required=False, type=int, many=True
    ),
    OpenApiParameter(
        name='tags', description='Filter by tags', required=False, type=int, many=True
    ),
])
class QuestionaryListView(ListMixin, ListAPIView):
    """
    API view to retrieve a list of all questionaries.
    """
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)

    async def get_queryset(self):
        qs = Questionary.objects.all()
        categories = self.request.query_params.getlist("categories")
        tags = self.request.query_params.getlist("tags")
        if categories:
            qs = qs.filter(categories__in=categories)
        if tags:
            qs = qs.filter(tags__in=tags)
        return qs.distinct()


class QuestionaryRetrieveView(RetrieveMixin, RetrieveAPIView):
    """
    API view to retrieve a single questionary by its ID.
    """
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryAnswerListView(ListMixin, ListAPIView):
    """
    API view to retrieve a list of all possible answers for questionary questions.
    """
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)


class QuestionaryResponseListCreateView(
    OwnedList, ListCreateMixin, ListCreateAPIView
):
    """
    API view to list and create questionary responses.
    Uses ownership filtering.
    """
    queryset = QuestionaryResponse.objects.all()
    permission_classes = (IsResponsePublic,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return QuestionaryResponseReadOnlySerializer
        return QuestionaryResponseSerializer


class QuestionaryResponseRetrieveUpdateView(
    ReadUpdateMixin, GenericAPIView
):
    """
    API view to retrieve and update a single questionary response by its ID.
    Uses ownership access.
    """
    queryset = QuestionaryResponse.objects.all()
    permission_classes = (IsResponsePublic,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return QuestionaryResponseReadOnlySerializer
        return QuestionaryResponseSerializer
    
    async def get_object(self):
        obj = await TagScreening.objects.aget(pk=self.kwargs["pk"])
        for permission in self.get_permissions():
            if hasattr(permission, "has_object_permission"):
                if not await permission.has_object_permission(self.request, self, obj):
                    self.permission_denied(self.request)
        return obj


class SurveyListView(ListMixin, ListAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyRetrieveView(RetrieveMixin, RetrieveAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeListCreateView(ListCreateMixin, ListCreateAPIView):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeRetrieveUpdateDestroyView(RetrieveUpdateDestroyMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultCreateView(CreateMixin, CreateAPIView):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultRetrieveUpdateView(ReadUpdateMixin, RetrieveUpdateAPIView):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryCreateView(CreateMixin, CreateAPIView):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryRetrieveUpdateDestroyView(RetrieveUpdateDestroyMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
