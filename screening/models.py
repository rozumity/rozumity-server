import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models

from rozumity.utils import rel


class CategoryQuestionary(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Questionary Category')
        verbose_name_plural = _('Questionary Categories')

    def __str__(self):
        return self.title


# TODO: caching property
class Questionary(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, default="")
    description = models.TextField(default="")
    category = models.ForeignKey(
        CategoryQuestionary, on_delete=models.CASCADE,
        related_name="questionaries", null=True, db_index=True
    )

    class Meta:
        verbose_name = _('Questionary')
        verbose_name_plural = _('Questionaries')

    def __str__(self):
        return self.title


class QuestionaryDimension(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Questionary Dimension')
        verbose_name_plural = _('Questionary Dimensions')

    def __str__(self):
        return self.title


class QuestionaryDimensionScore(models.Model):
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE,
        null=True, related_name="results"
    )
    min_score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)


class QuestionaryQuestion(models.Model):
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, 
        related_name="questions", null=True, db_index=True
    )
    title = models.CharField(max_length=255, default="")
    text = models.TextField(default="")
    weight = models.FloatField(default=1.0)
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE, 
        related_name="questions", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Question')
        verbose_name_plural = _('Questionary Questions')
        indexes = [
            models.Index(fields=["questionary", "dimension"]),
        ]
        unique_together = ('questionary', 'dimension')

    def __str__(self):
        return self.title


class QuestionaryAnswer(models.Model):
    question = models.ForeignKey(
        QuestionaryQuestion, on_delete=models.CASCADE, 
        related_name="answers", db_index=True
    )
    title = models.CharField(max_length=255, default="")
    value = models.FloatField()

    class Meta:
        verbose_name = _('Questionary Answer')
        verbose_name_plural = _('Questionary Answers')

    def __str__(self):
        return self.title

    async def rel(self, field_name:str=""):
        return await rel(self, field_name)


class QuestionaryResult(models.Model):
    title = models.CharField(max_length=128, default="")
    description = models.TextField(default="")
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, db_index=True, null=True,
        related_name="questionary_results"
    )
    scores = models.ForeignKey(
        QuestionaryDimensionScore, on_delete=models.CASCADE,
        null=True, related_name="results"
    )

    class Meta:
        verbose_name = _('Questionary Result')
        verbose_name_plural = _('Questionary Results')

    def __str__(self):
        return f"{self.client_id} {self.result_info.questionary_id}"


class QuestionaryResponse(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        unique=True, editable=False
    )
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="questionary_results",
        db_index=True
    )
    result = models.ForeignKey(
        QuestionaryResult, on_delete=models.CASCADE, null=True,
        related_name="responses"
    )
    answers = models.ManyToManyField(QuestionaryAnswer, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Questionary Result')
        verbose_name_plural = _('Questionary Results')

    def __str__(self):
        return f"{self.client_id} {self.result_info.questionary_id}"
    
    async def rel(self, field_name:str=""):
        return await rel(self, field_name)

    async def get_score(self, dimension_id):
        score = 0
        async for answer in await self.answers:
            question = await answer.rel("question")
            if question.dimension_id == dimension_id:
                score += answer.value
        return score

# Survey

class CategorySurvey(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Questionary Category')
        verbose_name_plural = _('Questionary Categories')

    def __str__(self):
        return self.title


class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

    def __str__(self):
        return self.title


class SurveyTheme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="themes")
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Survey Theme')
        verbose_name_plural = _('Survey Themes')

    def __str__(self):
        return self.title


class SurveyResult(models.Model):
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="survey_entries",
        db_index=True
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="results", db_index=True)
    completed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Survey Result')
        verbose_name_plural = _('Survey Results')
        indexes = [
            models.Index(fields=["client", "survey",]),
        ]

    def __str__(self):
        return f"{self.client.client_id}, {self.survey.survey_id}"


class SurveyEntry(models.Model):
    theme = models.ForeignKey(
        SurveyTheme, on_delete=models.CASCADE, 
        related_name="entries", db_index=True
    )
    result = models.ForeignKey(
        SurveyResult, on_delete=models.CASCADE, 
        related_name="entries", db_index=True
    )
    answer = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Survey Entry')
        verbose_name_plural = _('Survey Entries')
        unique_together = ("theme", "result")
        indexes = [
            models.Index(fields=["theme", "result"]),
        ]

    def __str__(self):
        return f"{self.theme.title}, {self.result.client_id}"
