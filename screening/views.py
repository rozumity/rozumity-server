from adrf.generics import *
from rozumity.mixins.caching_mixins import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rozumity.permissions import *
from rozumity.mixins.filtering_mixins import OwnedList
from screening.permissions import *

from screening.models import *
from screening.serializers import *


class CategoryQuestionaryListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all questionary categories.
    """
    queryset = CategoryQuestionary.objects.all()
    serializer_class = CategoryQuestionarySerializer
    permission_classes = (IsUser,)


class CategoryQuestionaryRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single questionary category by its ID.
    """
    queryset = CategoryQuestionary.objects.all()
    serializer_class = CategoryQuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all questionaries.
    """
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single questionary by its ID.
    """
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer
    permission_classes = (IsUser,)


class QuestionaryDimensionListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all questionary dimensions.
    """
    queryset = QuestionaryDimension.objects.all()
    serializer_class = QuestionaryDimensionSerializer
    permission_classes = (IsUser,)


class QuestionaryDimensionRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single questionary dimension by its ID.
    """
    queryset = QuestionaryDimension.objects.all()
    serializer_class = QuestionaryDimensionSerializer
    permission_classes = (IsUser,)


class QuestionaryQuestionListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all questions for questionaries.
    """
    queryset = QuestionaryQuestion.objects.all()
    serializer_class = QuestionaryQuestionSerializer
    permission_classes = (IsUser,)


class QuestionaryQuestionRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single question for a questionary by its ID.
    """
    queryset = QuestionaryQuestion.objects.all()
    serializer_class = QuestionaryQuestionSerializer
    permission_classes = (IsUser,)


class QuestionaryAnswerListCreateView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all possible answers for questionary questions.
    """
    queryset = QuestionaryAnswer.objects.all()
    serializer_class = QuestionaryAnswerSerializer
    permission_classes = (IsUser,)


class QuestionaryAnswerRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single answer for a questionary question by its ID.
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
    serializer_class = QuestionaryResponseSerializer
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


class SurveyListView(
    ListMixin, ListAPIView
):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeListCreateView(
    ListCreateMixin, ListCreateAPIView
):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyThemeRetrieveUpdateDestroyView(RetrieveUpdateDestroyMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyTheme.objects.all()
    serializer_class = SurveyThemeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultCreateView(
    CreateMixin, CreateAPIView
):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyResultRetrieveUpdateView(
    ReadUpdateMixin, RetrieveUpdateAPIView
):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryCreateView(
    CreateMixin, CreateAPIView
):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SurveyEntryRetrieveUpdateDestroyView(RetrieveUpdateDestroyMixin, RetrieveUpdateDestroyAPIView):
    queryset = SurveyEntry.objects.all()
    serializer_class = SurveyEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
