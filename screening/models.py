import uuid

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models

from django_ckeditor_5.fields import CKEditor5Field as RichTextField


class TagScreening(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = RichTextField(blank=True, null=True, max_length=2000)
    color = models.CharField(max_length=7, default="#FFFFFF")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class CategoryScreening(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = RichTextField(blank=True, default="", max_length=5000)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.title


class Questionary(models.Model):
    title = models.CharField(max_length=255, unique=True, default='', db_index=True)
    description = RichTextField(blank=True, null=True, max_length=5000)
    categories = models.ManyToManyField(CategoryScreening, blank=True, through='QuestionaryCategoryThrough')
    tags = models.ManyToManyField(TagScreening, blank=True, through='QuestionaryTagThrough')

    class Meta:
        ordering = ('title',)
        verbose_name = _('Questionary')
        verbose_name_plural = _('Questionaries')

    def __str__(self):
        return self.title


class QuestionaryQuestion(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, 
        related_name="questions", null=True, default=None, db_index=True
    )
    text = RichTextField(blank=True, null=True, max_length=5000)
    weight = models.FloatField(default=1.0)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        constraints = (
            models.UniqueConstraint(
                fields=['questionary', 'title'], 
                name='unique_question_per_questionary'
            ),
        )
        indexes = (models.Index(fields=['questionary']),)

    def __str__(self):
        return self.title


class QuestionaryDimension(models.Model):
    title = models.CharField(max_length=255, default="", unique=True, db_index=True)
    description = RichTextField(blank=True, null=True, max_length=2000)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Dimension')
        verbose_name_plural = _('Dimensions')

    def __str__(self):
        return self.title


class QuestionaryAnswer(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    question = models.ForeignKey(
        QuestionaryQuestion, on_delete=models.CASCADE, 
        related_name="answers", db_index=True
    )
    dimensions = models.ManyToManyField(
        QuestionaryDimension, blank=True, through='QuestionaryDimensionValue'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        constraints = (
            models.UniqueConstraint(
                fields=['question', 'title'],
                name='unique_answer_per_question'
            ),
        )
        indexes = (models.Index(fields=['question']),)

    def __str__(self):
        return self.title


class QuestionaryScore(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    description = RichTextField(blank=True, null=True, max_length=5000)
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
        verbose_name_plural = _('Scores')
        constraints = (
            models.UniqueConstraint(
                fields=['questionary', 'dimension', 'title'], 
                name='unique_score_per_questionary_dimension'
            ),
        )
        indexes = (models.Index(fields=['questionary', 'dimension']),)

    def __str__(self):
        return self.title

    def clean(self):
        if self.min_score > self.max_score:
            raise ValidationError("min_score cannot be greater than max_score")


class QuestionaryScoreExtra(models.Model):
    title = models.CharField(max_length=255, default="", db_index=True)
    description = RichTextField(blank=True, null=True, max_length=5000)
    questionary = models.ForeignKey(
        'Questionary', on_delete=models.CASCADE,
        related_name="score_extras", db_index=True
    )
    scores = models.ManyToManyField(
        QuestionaryScore, blank=True, through='QuestionaryScoreExtraThrough'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = _('Score Extra')
        verbose_name_plural = _('Score extras')
        indexes = (models.Index(fields=['questionary']),)

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
    answers = models.ManyToManyField(
        QuestionaryAnswer, blank=True,
        through='QuestionaryResponseAnswerThrough'
    )
    scores = models.ManyToManyField(
        QuestionaryScore, blank=True,
        through='QuestionaryResponseScoreThrough'
    )
    scores_extra = models.ManyToManyField(
        QuestionaryScoreExtra, blank=True,
        through='QuestionaryResponseScoreExtraThrough'
    )
    scores_map = models.JSONField(default=dict)
    is_filled = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_public_expert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)
        verbose_name = _('Response')
        verbose_name_plural = _('Responses')
        indexes = (models.Index(fields=['client', 'questionary']),)

    def __str__(self):
        return f"{self.client.user.email} - {self.questionary.title}"

    @property
    async def ais_empty(self):
        return not await self.answers.acount() and not await self.scores.acount()


# --- QUESTIONARY THROUGH ---

class QuestionaryDimensionValue(models.Model):
    answer = models.ForeignKey(
        QuestionaryAnswer, on_delete=models.CASCADE,
        related_name="dimension_values", db_index=True
    )
    dimension = models.ForeignKey(
        QuestionaryDimension, on_delete=models.CASCADE, 
        related_name="dimension_values", db_index=True
    )
    value = models.FloatField(default=0)

    class Meta:
        verbose_name = _('Value')
        verbose_name_plural = _('Values')
        constraints = (
            models.UniqueConstraint(
                fields=['dimension', 'value'], name='unique_dimension_value'
            ),
            models.UniqueConstraint(
                fields=['answer', 'dimension'], name='unique_answer_dimension'
            )
        )
        indexes = (models.Index(fields=['answer', 'dimension']),)

    def __str__(self):
        return f'{self.answer.title} {self.dimension.title} = {self.value}'


class QuestionaryCategoryThrough(models.Model):
    category = models.ForeignKey(
        CategoryScreening, on_delete=models.CASCADE,
        related_name='questionary_to_category', db_index=True
    )
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE,
        related_name='questionary_to_category', db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Category')
        verbose_name_plural = _('Questionary Categories')
        indexes = (models.Index(fields=['questionary', 'category']),)

    def __str__(self):
        return f'{self.category.title} - {self.questionary.title}'


class QuestionaryTagThrough(models.Model):
    tag = models.ForeignKey(
        TagScreening, on_delete=models.CASCADE,
        related_name="questionary_to_tag", db_index=True
    )
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE,
        related_name="questionary_to_tag", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Tag')
        verbose_name_plural = _('Questionary Tags')
        indexes = (models.Index(fields=['questionary', 'tag']),)

    def __str__(self):
        return f'{self.questionary.title} - {self.tag.title}'


class QuestionaryScoreExtraThrough(models.Model):
    score = models.ForeignKey(
        QuestionaryScore, on_delete=models.CASCADE,
        related_name="score_to_score_extra", db_index=True
    )
    score_extra = models.ForeignKey(
        QuestionaryScoreExtra, on_delete=models.CASCADE,
        related_name="score_to_score_extra", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Scores')
        verbose_name_plural = _('Questionary Scores')
        indexes = (models.Index(fields=['score', 'score_extra']),)

    def __str__(self):
        return f'{self.score.pk} - {self.score_extra.pk}'


class QuestionaryResponseAnswerThrough(models.Model):
    answer = models.ForeignKey(
        QuestionaryAnswer, on_delete=models.CASCADE,
        related_name="response_to_answer", db_index=True
    )
    response = models.ForeignKey(
        QuestionaryResponse, on_delete=models.CASCADE,
        related_name="response_to_answer", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Response Answer')
        verbose_name_plural = _('Questionary Response Answers')
        indexes = (models.Index(fields=['answer', 'response']),)
        constraints = (
            models.UniqueConstraint(
                fields=['answer', 'response'],
                name='unique_answer_per_response'
            ),
        )

    def __str__(self):
        return f'{self.answer.title} - {self.response.pk}'


class QuestionaryResponseScoreThrough(models.Model):
    score = models.ForeignKey(
        QuestionaryScore, on_delete=models.CASCADE,
        related_name="response_to_score", db_index=True
    )
    response = models.ForeignKey(
        QuestionaryResponse, on_delete=models.CASCADE,
        related_name="response_to_score", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Response Score')
        verbose_name_plural = _('Questionary Response Scores')
        indexes = (models.Index(fields=['score', 'response']),)

    def __str__(self):
        return f'{self.score.dimension.title}: {self.score.min_score}-{self.score.max_score}'


class QuestionaryResponseScoreExtraThrough(models.Model):
    score_extra = models.ForeignKey(
        QuestionaryScoreExtra, on_delete=models.CASCADE,
        related_name="response_to_score_extra", db_index=True
    )
    response = models.ForeignKey(
        QuestionaryResponse, on_delete=models.CASCADE,
        related_name="response_to_score_extra", db_index=True
    )

    class Meta:
        verbose_name = _('Questionary Response Score Extra')
        verbose_name_plural = _('Questionary Response Score Extras')
        indexes = (models.Index(fields=['response', 'score_extra']),)

    def __str__(self):
        return str(self.score_extra.pk)


# --- SURVEYS ---

class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, default="", db_index=True)
    description = RichTextField(blank=True, null=True, max_length=5000)
    categories = models.ManyToManyField(CategoryScreening, blank=True)
    tags = models.ManyToManyField(TagScreening, blank=True)

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

    def __str__(self):
        return self.title


class SurveyTheme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="themes", db_index=True)
    title = models.CharField(max_length=255, default="", db_index=True)
    description = models.TextField(default="", max_length=1000)

    class Meta:
        verbose_name = _('Theme')
        verbose_name_plural = _('Survey themes')
        constraints = (
            models.UniqueConstraint(
                fields=['survey', 'title'], name='unique_theme_per_survey'
            ),
        )
        indexes = (models.Index(fields=['survey']),)

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
        verbose_name_plural = _('Survey results')
        indexes = (models.Index(fields=['client', 'survey']),)

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
    answer = RichTextField(blank=True, null=True, max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Entry')
        verbose_name_plural = _('Survey entries')
        constraints = (
            models.UniqueConstraint(
                fields=['theme', 'result'], 
                name='unique_entry_per_theme_result'
            ),
        )
        indexes = (models.Index(fields=['theme', 'result']),)

    def __str__(self):
        return f"{self.theme.title}, {self.result.client.pk}"
