from rest_framework import serializers
from accounts.serializers import ClientProfileSerializer
from accounts.models import ClientProfile
from screening.models import *
from rozumity.mixins.serialization_mixins import ReadOnlySerializerMixin


class CategoryQuestionarySerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = CategoryQuestionary
        fields = "__all__"


class QuestionarySerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    category = CategoryQuestionarySerializer()

    class Meta:
        model = Questionary
        fields = "__all__"


class QuestionaryDimensionSerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = QuestionaryDimension
        fields = "__all__"


class QuestionaryQuestionSerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryQuestion
        fields = "__all__"


class QuestionaryAnswerSerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    question = QuestionaryQuestionSerializer()
    dimension = QuestionaryDimensionSerializer()

    class Meta:
        model = QuestionaryAnswer
        fields = "__all__"


class QuestionaryResultSerializer(serializers.ModelSerializer):
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryResult
        fields = "__all__"


class QuestionaryResponseSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = serializers.PrimaryKeyRelatedField(queryset=Questionary.objects.all())
    result = serializers.PrimaryKeyRelatedField(queryset=QuestionaryResult.objects.all())
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=QuestionaryAnswer.objects.all())

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"


class QuestionaryResponseReadOnlySerializer(
    ReadOnlySerializerMixin, QuestionaryResponseSerializer
):
    class AnswerSerializer(
        ReadOnlySerializerMixin, serializers.ModelSerializer
    ):
        class QuestionSerializer(
            ReadOnlySerializerMixin, serializers.ModelSerializer
        ):
            class Meta:
                model = QuestionaryQuestion
                fields = ("id", "title")

        question = QuestionSerializer()
        dimension = QuestionaryDimensionSerializer()

        class Meta:
            model = QuestionaryAnswer
            fields = "__all__"

    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = QuestionarySerializer()
    result = QuestionaryResultSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class SurveyThemeSerializer(serializers.ModelSerializer):
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = SurveyTheme
        fields = "__all__"


class SurveyResultSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = SurveyResult
        fields = "__all__"


class SurveyEntrySerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=SurveyTheme.objects.all())
    result = serializers.PrimaryKeyRelatedField(queryset=SurveyResult.objects.all())

    class Meta:
        model = SurveyEntry
        fields = "__all__"
