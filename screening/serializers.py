from rest_framework import serializers
from adrf.serializers import ModelSerializer
from accounts.serializers import ClientProfileSerializer
from accounts.models import ClientProfile
from screening.models import *
from rozumity.mixins.serialization_mixins import ReadOnlySerializerMixin


class TagScreeningSerializer(ReadOnlySerializerMixin, ModelSerializer):
    class Meta:
        model = TagScreening
        fields = "__all__"


class CategoryScreeningSerializer(ReadOnlySerializerMixin, ModelSerializer):
    class Meta:
        model = CategoryScreening
        fields = "__all__"


class QuestionaryDimensionSerializer(ReadOnlySerializerMixin, ModelSerializer):
    class Meta:
        model = QuestionaryDimension
        fields = "__all__"


class QuestionaryDimensionValueSerializer(ReadOnlySerializerMixin, ModelSerializer):
    dimension = QuestionaryDimensionSerializer()

    class Meta:
        model = QuestionaryDimensionValue
        exclude = ('answer',)


class QuestionarySerializer(ReadOnlySerializerMixin, ModelSerializer):
    class QuestionsSerializer(ReadOnlySerializerMixin, ModelSerializer):
        class AnswerSerializer(ReadOnlySerializerMixin, ModelSerializer):
            class Meta:
                model, exclude = QuestionaryAnswer, ['question', 'dimensions']
        answers = AnswerSerializer(many=True, read_only=True)
        class Meta:
            model, exclude = QuestionaryQuestion, ['questionary']

    categories = CategoryScreeningSerializer(many=True)
    tags = TagScreeningSerializer(many=True)
    questions = QuestionsSerializer(many=True)

    class Meta:
        model = Questionary
        fields = "__all__"


class QuestionaryScoreSerializer(ReadOnlySerializerMixin, ModelSerializer):
    dimension = QuestionaryDimensionSerializer()
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryScore
        fields = "__all__"


class QuestionaryScoreExtraSerializer(ReadOnlySerializerMixin, ModelSerializer):
    scores = QuestionaryScoreSerializer(many=True)
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryScoreExtra
        fields = "__all__"


class QuestionaryQuestionSerializer(ReadOnlySerializerMixin, ModelSerializer):
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryQuestion
        fields = "__all__"


class QuestionaryAnswerSerializer(ReadOnlySerializerMixin, ModelSerializer):
    question = QuestionaryQuestionSerializer()
    values = QuestionaryDimensionValueSerializer(many=True, source='dimension_values')

    class Meta:
        model = QuestionaryAnswer
        fields = "__all__"


class QuestionaryResponseSerializer(ModelSerializer):
    class QuestionaryScoreSerializer(ReadOnlySerializerMixin, ModelSerializer):
        dimension = QuestionaryDimensionSerializer()
        class Meta:
            model = QuestionaryScore
            exclude = ('questionary',)
    class QuestionaryScoreExtraSerializer(ReadOnlySerializerMixin, ModelSerializer):
        class Meta:
            model = QuestionaryScore
            fields = "__all__"


    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = serializers.PrimaryKeyRelatedField(queryset=Questionary.objects.all(), required=False)
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=QuestionaryAnswer.objects.all(), required=False)
    scores = QuestionaryScoreSerializer(many=True, read_only=True)
    scores_extra=QuestionaryScoreExtraSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionaryResponse
        exclude = ('scores_map',)

    async def aupdate(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        if answers_data and isinstance(answers_data, list) and len(answers_data):
            instance._answers_from_request = answers_data  # для сигнала
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        await instance.asave()
        return instance


class SurveySerializer(ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=CategoryScreening.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=TagScreening.objects.all())

    class Meta:
        model = Survey
        fields = "__all__"


class SurveyThemeSerializer(ModelSerializer):
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = SurveyTheme
        fields = "__all__"


class SurveyResultSerializer(ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = SurveyResult
        fields = "__all__"


class SurveyEntrySerializer(ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=SurveyTheme.objects.all())
    result = serializers.PrimaryKeyRelatedField(queryset=SurveyResult.objects.all())

    class Meta:
        model = SurveyEntry
        fields = "__all__"
