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


class QuestionaryCategorySerializer(ReadOnlySerializerMixin, ModelSerializer):
    class Meta:
        model = QuestionaryCategory
        fields = "__all__"


class QuestionaryDimensionSerializer(ReadOnlySerializerMixin, ModelSerializer):
    class Meta:
        model = QuestionaryDimension
        fields = "__all__"


class QuestionaryDimensionValueSerializer(ReadOnlySerializerMixin, ModelSerializer):
    dimension = QuestionaryDimensionSerializer()

    class Meta:
        model = QuestionaryDimensionValue
        fields = "__all__"


class QuestionarySerializer(ReadOnlySerializerMixin, ModelSerializer):
    categories = QuestionaryCategorySerializer(many=True)
    tags = TagScreeningSerializer(many=True)

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
    values = QuestionaryDimensionValueSerializer(many=True)

    class Meta:
        model = QuestionaryAnswer
        fields = "__all__"


class QuestionaryResponseSerializer(ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = serializers.PrimaryKeyRelatedField(queryset=Questionary.objects.all())
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=QuestionaryAnswer.objects.all())

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"

    async def aupdate(self, instance, validated_data):
        if validated_data.get('answers', []):
            await instance.answers.aadd(set(
                [a.pk if hasattr(a, 'pk') else a for a in validated_data['answers']]
            ))
        instance = await super().aupdate(self, instance, validated_data)
        if await instance.is_filled:
            total_score = await instance.total_score  # {dimension_id: score}
            candidate_qs = QuestionaryScore.objects.filter(
                questionary=instance.questionary
            )
            for dim_id, score in total_score.items():
                candidate_qs = candidate_qs.filter(
                    dimension_id=dim_id, min_score__lte=score, max_score__gte=score
                )
            candidate_qs = candidate_qs.distinct()
            result = await candidate_qs.afirst()
            if result:
                instance.result = result
                await instance.asave()
        return instance


class QuestionaryResponseReadOnlySerializer(ReadOnlySerializerMixin, QuestionaryResponseSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    questionary = QuestionarySerializer()
    answers = QuestionaryAnswerSerializer(many=True)

    class Meta:
        model = QuestionaryResponse
        fields = "__all__"


class SurveySerializer(ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=SurveyCategory.objects.all())
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
