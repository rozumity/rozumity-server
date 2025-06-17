import uuid

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from asgiref.sync import sync_to_async


class TagScreening(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = models.TextField(default="")
    color = models.CharField(max_length=7, default="#FFFFFF")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class QuestionaryCategory(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = models.TextField(default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Category Questionary')
        verbose_name_plural = _('Q - Categories')

    def __str__(self):
        return self.title


class QuestionaryDimension(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = models.TextField(default="")

    class Meta:
        ordering = ('title',)
        verbose_name = _('Dimension')
        verbose_name_plural = _('Q - Dimensions')

    def __str__(self):
        return self.title


class QuestionaryDimensionValue(models.Model):
    value = models.FloatField(default=0)
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE, 
        related_name="dimension_values", db_index=True
    )

    class Meta:
        ordering = ('value',)
        verbose_name = _('Value')
        verbose_name_plural = _('Q - Values')
        constraints = [
            models.UniqueConstraint(fields=['dimension', 'value'], name='unique_dimension_value')
        ]
        indexes = [
            models.Index(fields=['dimension']),
        ]

    def __str__(self):
        return f'{self.dimension.title} +{self.value}'


class QuestionaryScore(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    description = models.TextField(default="")
    questionary = models.ForeignKey(
        'Questionary', on_delete=models.CASCADE, related_name="scores",
        null=True, default=None, db_index=True
    )
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE, related_name="scores",
        null=True, default=None, db_index=True
    )
    min_score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Score')
        verbose_name_plural = _('Q - Scores')
        constraints = [
            models.UniqueConstraint(
                fields=['questionary', 'dimension', 'title'], 
                name='unique_score_per_questionary_dimension'
            )
        ]
        indexes = [
            models.Index(fields=['questionary', 'dimension']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.min_score > self.max_score:
            raise ValidationError("min_score cannot be greater than max_score")


class QuestionaryScoreExtra(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    description = models.TextField(default="")
    questionary = models.ForeignKey(
        'Questionary', on_delete=models.CASCADE,
        related_name="score_extras", db_index=True
    )
    scores = models.ManyToManyField(QuestionaryScore, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Score Extra')
        verbose_name_plural = _('Q - Extras')
        indexes = [
            models.Index(fields=['questionary']),
        ]

    def __str__(self):
        return self.title


class Questionary(models.Model):
    title = models.CharField(max_length=255, unique=True, default="", db_index=True)
    description = models.TextField(default="")
    categories = models.ManyToManyField(QuestionaryCategory, blank=True)
    tags = models.ManyToManyField(TagScreening, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Questionary')
        verbose_name_plural = _('Q - Questionaries')

    def __str__(self):
        return self.title


class QuestionaryQuestion(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, 
        related_name="questions", null=True, default=None, db_index=True
    )
    text = models.TextField(default="")
    weight = models.FloatField(default=1.0)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Question')
        verbose_name_plural = _('Q - Questions')
        constraints = [
            models.UniqueConstraint(fields=['questionary', 'title'], name='unique_question_per_questionary')
        ]
        indexes = [
            models.Index(fields=['questionary']),
        ]

    def __str__(self):
        return self.title


class QuestionaryAnswer(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    question = models.ForeignKey(
        QuestionaryQuestion, on_delete=models.CASCADE, 
        related_name="answers", db_index=True
    )
    values = models.ManyToManyField(QuestionaryDimensionValue, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Q - Answers')
        constraints = [
            models.UniqueConstraint(fields=['question', 'title'], name='unique_answer_per_question')
        ]
        indexes = [
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return self.title


class QuestionaryResponse(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        unique=True, editable=False
    )
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        related_name="responses", null=True, db_index=True
    )
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE,
        related_name="responses", null=True, db_index=True
    )
    answers = models.ManyToManyField(QuestionaryAnswer, blank=True)
    scores = models.ManyToManyField(QuestionaryScore, blank=True)
    scores_extra = models.ManyToManyField(QuestionaryScoreExtra, blank=True)
    is_filled = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_public_expert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)
        verbose_name = _('Response')
        verbose_name_plural = _('Q - Responses')
        indexes = [
            models.Index(fields=['client', 'questionary'])
        ]

    def __str__(self):
        return f"{self.client.pk} - {self.questionary.title}"

    @property
    async def is_filled(self):
        is_filled = self.__dict__['is_filled']
        if is_filled:
            return True
        questions_q = self.questionary.questions.all()
        answers_q = self.answers.all()
        if await answers_q.acount() >= await questions_q.acount():
            is_filled = set(
                await questions_q.values_list("id", flat=True)
            ).issubset(set(
                await answers_q.values_list("question_id", flat=True)
            ))
            await sync_to_async(super().__setattr__)('is_filled', is_filled)
        return is_filled

    # TODO: generate json from the actual scores, and by dimension id
    @property
    async def scores_map(self):
        scores = self.__dict__['scores']
        is_filled = self.__dict__['is_filled']
        return scores
    

class SurveyCategory(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = models.TextField(default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Category Survey')
        verbose_name_plural = _('S - Categories')

    def __str__(self):
        return self.title


class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, default="", db_index=True)
    description = models.TextField(default="")
    categories = models.ManyToManyField(
        SurveyCategory, blank=True
    )
    tags = models.ManyToManyField(
        TagScreening, blank=True
    )

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('S - Surveys')

    def __str__(self):
        return self.title


class SurveyTheme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="themes", db_index=True)
    title = models.CharField(max_length=255, default="", db_index=True)
    description = models.TextField(default="")

    class Meta:
        verbose_name = _('Theme')
        verbose_name_plural = _('S - Themes')
        constraints = [
            models.UniqueConstraint(fields=['survey', 'title'], name='unique_theme_per_survey')
        ]
        indexes = [
            models.Index(fields=['survey']),
        ]

    def __str__(self):
        return self.title


class SurveyResult(models.Model):
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        related_name="survey_entries", null=True, db_index=True
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="results", db_index=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('S - Results')
        indexes = [
            models.Index(fields=['client', 'survey']),
        ]

    def __str__(self):
        return f"{self.client.pk}, {self.survey.title}"


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
        constraints = [
            models.UniqueConstraint(
                fields=['theme', 'result'], 
                name='unique_entry_per_theme_result'
            )
        ]
        indexes = [
            models.Index(fields=['theme', 'result']),
        ]

    def __str__(self):
        return f"{self.theme.title}, {self.result.client.pk}"
