import uuid
from django.db import models


class Screening(models.Model):
    id = models.SlugField(primary_key=True, max_length=5, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class ScreeningCategory(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class ScreeningDimension(models.Model):
    id = models.SlugField(primary_key=True, max_length=5, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class ScreeningQuestion(models.Model):
    screening = models.ForeignKey(
        Screening, on_delete=models.CASCADE, 
        related_name="questions", db_index=True
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
    weight = models.FloatField(default=1.0)
    dimension = models.ForeignKey(
        ScreeningDimension, on_delete=models.CASCADE, 
        related_name="questions", db_index=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["screening", "dimension"]),
        ]
        unique_together = ('screening', 'dimension')

    def __str__(self):
        return self.title


class ScreeningAnswer(models.Model):
    question = models.ForeignKey(
        Screening, on_delete=models.CASCADE, 
        related_name="answers", db_index=True
    )
    title = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return self.title


class ScreeningResponse(models.Model):
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="screening_response",
        db_index=True
    )
    question = models.ForeignKey(
        ScreeningQuestion, on_delete=models.SET_NULL, null=True, db_index=True,
        related_name="screening_response"
    )
    answer = models.ForeignKey(
        ScreeningAnswer, on_delete=models.SET_NULL, null=True, db_index=True,
        related_name="screening_response"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("client", "question")
        indexes = [
            models.Index(fields=["client", "question"]),
        ]

    def __str__(self):
        return f"{self.question}, {self.client}"


class ScreeningResult(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, 
        unique=True, editable=False
    )
    client = models.ForeignKey(
        'accounts.ClientProfile', on_delete=models.PROTECT,
        null=True, blank=True, related_name="screening_results",
        db_index=True
    )
    result_info = models.ForeignKey(
        'ScreeningResultInfo', on_delete=models.CASCADE,
        null=True, blank=True, related_name="screening_result_info",
        db_index=True
    )
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.client_id} {self.result_info.screening_id}"


class ScreeningResultInfo(models.Model):
    screening = models.ForeignKey(
        Screening, on_delete=models.CASCADE,
        related_name="screening_possible_results"
    )
    min_score = models.FloatField()
    max_score = models.FloatField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, max_length=500)

    class Meta:
        unique_together = ("screening", "min_score", "max_score")
        indexes = [
            models.Index(fields=["screening", "min_score", "max_score"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.min_score}-{self.max_score}), {self.screening}"

# Survey

class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class SurveyTheme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="themes")
    title = models.TextField()
    description = models.TextField(blank=True, null=True)

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
        unique_together = ("theme", "result")
        indexes = [
            models.Index(fields=["theme", "result"]),
        ]

    def __str__(self):
        return f"{self.theme.title}, {self.result.client_id}"
