from rest_framework import serializers
from adrf.serializers import ModelSerializer
from accounts.serializers import ClientProfileSerializer
from accounts.models import ClientProfile
from screening.models import *
from rozumity.mixins.serialization_mixins import ReadOnlySerializerMixin


class CategoryQuestionarySerializer(
    ReadOnlySerializerMixin, ModelSerializer
):
    class Meta:
        model = CategoryQuestionary
        fields = "__all__"


class QuestionarySerializer(
    ReadOnlySerializerMixin, ModelSerializer
):
    categories = CategoryQuestionarySerializer(many=True)

    class Meta:
        model = Questionary
        fields = "__all__"


class QuestionaryDimensionSerializer(
    ReadOnlySerializerMixin, ModelSerializer
):
    class Meta:
        model = QuestionaryDimension
        fields = "__all__"


class QuestionaryQuestionSerializer(
    ReadOnlySerializerMixin, ModelSerializer
):
    questionary = QuestionarySerializer()

    class Meta:
        model = QuestionaryQuestion
        fields = "__all__"


class QuestionaryScoreSerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    dimension = QuestionaryDimensionSerializer()

    class Meta:
        model = QuestionaryScore
        fields = "__all__"


class QuestionaryAnswerValueSerializer(
    ReadOnlySerializerMixin, serializers.ModelSerializer
):
    dimension = QuestionaryDimensionSerializer()

    class Meta:
        model = QuestionaryAnswerValue
        fields = "__all__"


class QuestionaryAnswerSerializer(
    ReadOnlySerializerMixin, ModelSerializer
):
    question = QuestionaryQuestionSerializer()
    values = QuestionaryAnswerValueSerializer(many=True)

    class Meta:
        model = QuestionaryAnswer
        fields = "__all__"


class QuestionaryResponseSerializer(ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = serializers.PrimaryKeyRelatedField(queryset=Questionary.objects.all())
    result = serializers.PrimaryKeyRelatedField(queryset=QuestionaryResult.objects.all())
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=QuestionaryAnswer.objects.all())

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"

    async def aupdate(self, instance, validated_data):
        if 'answers' in validated_data and len(validated_data.get('answers')):
            async for answer in instance.answers.all():
                validated_data['answers'].append(answer)
        instance = await ModelSerializer.aupdate(self, instance, validated_data)
        if await instance.is_filled:
            total_score = await instance.total_score
            results = (
                QuestionaryResult.objects
                .annotate(scores_count=models.Count('scores'))
                .filter(scores_count=len(total_score))
            )
            for dim_id, score in total_score.items():
                results = results.filter(
                    scores__dimension_id=dim_id,
                    scores__min_score__lte=score,
                    scores__max_score__gte=score
                )
            result = await results.distinct().afirst()
            if result:
                instance = await ModelSerializer.aupdate(self, instance, {'result': result})
        return instance


class QuestionaryResponseReadOnlySerializer(
    ReadOnlySerializerMixin, QuestionaryResponseSerializer
):
    class QuestionaryResultReadOnlySerializer(ReadOnlySerializerMixin, ModelSerializer):
        scores = QuestionaryScoreSerializer(many=True)

        class Meta:
            model = QuestionaryResult
            exclude = ('questionary',)

    class QuestionaryAnswerReadOnlySerializer(ReadOnlySerializerMixin, ModelSerializer):
        class QuestionaryQuestionReadOnlySerializer(ReadOnlySerializerMixin, ModelSerializer):
            class Meta:
                model = QuestionaryQuestion
                exclude = ('questionary',)

        question = QuestionaryQuestionReadOnlySerializer()

        class Meta:
            model = QuestionaryAnswer
            exclude = ('values',)

    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = QuestionarySerializer()
    result = QuestionaryResultReadOnlySerializer()
    answers = QuestionaryAnswerReadOnlySerializer(many=True)

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"


class SurveySerializer(ModelSerializer):
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
