import uuid
from async_property import async_cached_property

from django.utils.translation import gettext_lazy as _
from django.db import models

from rozumity.utils import rel


class TagScreening(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    color = models.CharField(max_length=7, default="#FFFFFF")

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class CategoryQuestionary(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Category Questionary')
        verbose_name_plural = _('Q - Categories')

    def __str__(self):
        return self.title


class Questionary(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, default="")
    description = models.TextField(default="")
    categories = models.ManyToManyField(
        CategoryQuestionary, blank=True
    )
    tags = models.ManyToManyField(
        TagScreening, blank=True
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
        verbose_name = _('Dimension')
        verbose_name_plural = _('Q - Dimensions')

    def __str__(self):
        return self.title


class QuestionaryScore(models.Model):
    title = models.CharField(max_length=255, default="")
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE,
        null=True, related_name="results"
    )
    min_score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)

    class Meta:
        verbose_name = _('Score')
        verbose_name_plural = _('Q - Scores')

    def __str__(self):
        return self.title


class QuestionaryQuestion(models.Model):
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, 
        related_name="questions", null=True, db_index=True
    )
    title = models.CharField(max_length=255, default="")
    text = models.TextField(default="")
    weight = models.FloatField(default=1.0)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Q - Questions')

    def __str__(self):
        return self.title


class QuestionaryAnswerValue(models.Model):
    value = models.FloatField(default=0)
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE, 
        related_name="answers", db_index=True, null=True
    )

    class Meta:
        verbose_name = _('Value')
        verbose_name_plural = _('Q - Values')
        indexes = [
            models.Index(fields=["dimension", "value"]),
        ]
        unique_together = ('dimension', 'value')

    def __str__(self):
        return f'{self.dimension.title} +{self.value}'


class QuestionaryAnswer(models.Model):
    question = models.ForeignKey(
        QuestionaryQuestion, on_delete=models.CASCADE, 
        related_name="answers", db_index=True
    )
    title = models.CharField(max_length=255, default="")
    values = models.ManyToManyField(QuestionaryAnswerValue)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Q - Answers')

    def __str__(self):
        return self.title


class QuestionaryResult(models.Model):
    title = models.CharField(max_length=128, default="")
    description = models.TextField(default="")
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, db_index=True, null=True,
        related_name="results"
    )
    scores = models.ManyToManyField(QuestionaryScore, related_name="results")

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('Q - Results')

    def __str__(self):
        return f"{self.title} - {self.questionary.title}"


class QuestionaryResponse(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        unique=True, editable=False
    )
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, related_name="questionary_results",
        db_index=True
    )
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, null=True,
        related_name="responses"
    )
    result = models.ForeignKey(
        QuestionaryResult, on_delete=models.CASCADE, 
        null=True, blank=True, related_name="responses"
    )
    answers = models.ManyToManyField(
        QuestionaryAnswer, blank=True,
        related_name='responses'
    )
    is_public = models.BooleanField(default=False)
    is_public_expert = models.BooleanField(default=False)
    is_filled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Response')
        verbose_name_plural = _('Q - Responses')

    def __str__(self):
        title = "draft"
        if self.result:
            title = self.result.questionary.title
        return f"{self.client_id} - {title}"
    
    async def check_is_filled(self):
        questionary = await rel(self, 'questionary')
        questions = rel(questionary, 'questions')
        answers = await rel(self, 'answers')
        if await questions.objects.acount() == await answers.objects.acount():
            return {
                question.title async for question in questions
            } == {
                answer.question.id async for answer in answers
            }
        

    async def get_score_by_dimension(self, dimension_id):
        score = 0
        async for answer in await self.answers:
            async for value in answer.values:
                if value.dimension_id == dimension_id:
                    score += value.value
        return score

    @async_cached_property
    async def total_score(self):
        score = {}
        async for answer in await self.answers:
            weight = getattr(await rel(answer, 'question'), 'weight')
            async for value in answer.values:
                dim_id = value.dimension_id
                if dim_id not in score.keys():
                    score[dim_id] = 0
                score[dim_id] += value.value * weight
        return score

# Survey

class CategorySurvey(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Category Survey')
        verbose_name_plural = _('S - Categories')

    def __str__(self):
        return self.title


class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, default="")
    description = models.TextField(default="")
    categories = models.ManyToManyField(
        CategorySurvey, blank=True
    )
    tags = models.ManyToManyField(
        TagScreening, blank=True
    )

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
        verbose_name = _('Theme')
        verbose_name_plural = _('S - Themes')

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
        verbose_name = _('Result')
        verbose_name_plural = _('S - Results')
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
        verbose_name = _('Entry')
        verbose_name_plural = _('S - Entries')
        unique_together = ("theme", "result")
        indexes = [
            models.Index(fields=["theme", "result"]),
        ]

    def __str__(self):
        return f"{self.theme.title}, {self.result.client_id}"
