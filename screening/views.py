from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView
)
from rozumity.mixins.caching_mixins import (
    CacheRUDMixin, CacheRUMixin, CacheLCMixin, 
    CacheListMixin, CacheRetrieveMixin, CacheCreateMixin
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rozumity.permissions import *

from screening.models import *
from screening.serializers import *


class CategoryQuestionaryListView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = CategoryQuestionary.objects.all()
    serializer_class = CategoryQuestionarySerializer
    permission_classes = (IsUser,)


class CategoryQuestionaryRetrieveView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = CategoryQuestionary.objects.all()
    serializer_class = CategoryQuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryListView(
    CacheLCMixin, ListAPIView
):
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryDimensionListView(
    CacheListMixin, ListAPIView
):
    queryset = QuestionaryDimension.objects.all()
    serializer_class = QuestionaryDimensionSerializer
    permission_classes = (IsUser,)


class QuestionaryDimensionRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = QuestionaryDimension.objects.all()
    serializer_class = QuestionaryDimensionSerializer
    permission_classes = (IsUser,)


class QuestionaryQuestionListCreateView(
    CacheListMixin, ListAPIView
):
    queryset = QuestionaryQuestion.objects.all()
    serializer_class = QuestionaryQuestionSerializer
    permission_classes = (IsUser,)


class QuestionaryQuestionRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = QuestionaryQuestion.objects.all()
    serializer_class = QuestionaryQuestionSerializer
    permission_classes = (IsUser,)


class QuestionaryAnswerListCreateView(
    CacheListMixin, ListAPIView
):
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)


class QuestionaryAnswerRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)


class QuestionaryResponseCreateView(
    CacheCreateMixin, CreateAPIView
):
    queryset = QuestionaryResponse.objects.all()
    serializer_class = QuestionaryResponseSerializer
    permission_classes = (IsCreatorOwner,)


class QuestionaryResponseRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = QuestionaryResponse.objects.all()
    serializer_class = QuestionaryResponseSerializer
    permission_classes = (IsCreatorOwner,)


class QuestionaryResultCreateView(CacheCreateMixin, CreateAPIView):
    queryset = QuestionaryResult.objects.all()
    serializer_class = QuestionaryResultSerializer
    permission_classes = (IsCreatorOwner,)


class QuestionaryResultRetrieveUpdateView(CacheRUMixin, RetrieveUpdateAPIView):
    queryset = QuestionaryResult.objects.all()
    serializer_class = QuestionaryResultSerializer
    permission_classes = (IsCreatorOwner,)


class SurveyListCreateView(CacheLCMixin, ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyRetrieveUpdateDestroyView(CacheRUDMixin, RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeListCreateView(CacheLCMixin, ListCreateAPIView):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeRetrieveUpdateDestroyView(CacheRUDMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultListCreateView(CacheLCMixin, ListCreateAPIView):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultRetrieveUpdateDestroyView(CacheRUDMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryListCreateView(CacheLCMixin, ListCreateAPIView):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryRetrieveUpdateDestroyView(CacheRUDMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
