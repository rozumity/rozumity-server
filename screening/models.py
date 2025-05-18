import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models


class QuestionaryCategory(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Questionary Category')
        verbose_name_plural = _('Questionary Categories')

    def __str__(self):
        return self.title


# TODO: caching property
class Questionary(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        QuestionaryCategory, on_delete=models.CASCADE,
        related_name="questionaries", null=True, db_index=True
    )
    min_score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)

    class Meta:
        verbose_name = _('Questionary')
        verbose_name_plural = _('Questionaries')

    def __str__(self):
        return self.title


class QuestionaryDimension(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Questionary Dimension')
        verbose_name_plural = _('Questionary Dimensions')

    def __str__(self):
        return self.title


class QuestionaryQuestion(models.Model):
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, 
        related_name="questions", null=True, db_index=True
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
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
    title = models.CharField(max_length=255)
    value = models.FloatField()

    class Meta:
        verbose_name = _('Questionary Answer')
        verbose_name_plural = _('Questionary Answers')

    def __str__(self):
        return self.title


class QuestionaryResult(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, 
        unique=True, editable=False
    )
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="questionary_results",
        db_index=True
    )
    questionary = models.ForeignKey(
        Questionary, on_delete=models.CASCADE, db_index=True, null=True,
        related_name="questionary_results"
    )
    scores = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Questionary Result')
        verbose_name_plural = _('Questionary Results')

    def __str__(self):
        return f"{self.client_id} {self.result_info.questionary_id}"


class QuestionaryResponse(models.Model):
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="questionary_response",
        db_index=True
    )
    result = models.ForeignKey(
        QuestionaryResult, on_delete=models.CASCADE, null=True, db_index=True,
        related_name="questionary_response"
    )
    question = models.ForeignKey(
        QuestionaryQuestion, on_delete=models.SET_NULL, null=True, db_index=True,
        related_name="questionary_response"
    )
    answer = models.ForeignKey(
        QuestionaryAnswer, on_delete=models.SET_NULL, null=True, db_index=True,
        related_name="questionary_response"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Questionary Response')
        verbose_name_plural = _('Questionary Responses')
        unique_together = ("client", "question")
        indexes = [
            models.Index(fields=["client", "question"]),
        ]

    def __str__(self):
        return f"{self.question}, {self.client}"

# Survey

class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

    def __str__(self):
        return self.title


class SurveyTheme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="themes")
    title = models.TextField()
    description = models.TextField(blank=True, null=True)

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
    answer = models.TextField()
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
