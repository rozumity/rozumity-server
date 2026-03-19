import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field as RichTextField


class TagScreening(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    color = models.CharField(max_length=7, default="#FFFFFF")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class CategoryScreening(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.title


class Questionary(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    description = RichTextField(blank=True, null=True)
    categories = models.ManyToManyField(CategoryScreening, blank=True)
    tags = models.ManyToManyField(TagScreening, blank=True)
    version = models.IntegerField(default=1)

    class Meta:
        verbose_name = _('Questionary')
        verbose_name_plural = _('Questionaries')

    def __str__(self):
        return self.title


class QuestionaryDimension(models.Model):
    title = models.CharField(max_length=255, unique=True)
    
    class Meta:
        verbose_name = _('Dimension')
        verbose_name_plural = _('Dimensions')

    def __str__(self):
        return self.title


class QuestionaryBlock(models.Model):
    questionary = models.ForeignKey(
        'Questionary', 
        on_delete=models.CASCADE, 
        related_name="blocks"
    )
    title = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)
        verbose_name = _('Block')
        verbose_name_plural = _('Blocks')

    def __str__(self):
        return f"{self.questionary.title} - {self.title or self.order}"


class QuestionaryQuestion(models.Model):
    block = models.ForeignKey(
        QuestionaryBlock, 
        on_delete=models.CASCADE, 
        related_name="questions"
    )
    questionary = models.ForeignKey(
        'Questionary', 
        on_delete=models.CASCADE, 
        related_name="questions"
    )
    text = RichTextField(max_length=5000)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        constraints = [
            models.UniqueConstraint(
                fields=['block', 'questionary', 'order'], 
                name='unique_question_in_block_order'
            )
        ]

    def __str__(self):
        return f"{self.questionary.title} - {self.block.title} - {self.order}"

    def clean(self):
        """
        Strict validation for Python/Admin level.
        """
        super().clean()
        if not self.block_id or not self.questionary_id:
            return
        if self.block.questionary_id != self.questionary_id:
            raise ValidationError({
                'block': _("The selected block belongs to a different questionnaire."),
                'questionary': _("The questionnaire does not match the parent block's questionnaire.")
            })


class QuestionaryAnswer(models.Model):
    question = models.ForeignKey(
        QuestionaryQuestion, 
        on_delete=models.CASCADE, 
        related_name="answers"
    )
    text = models.CharField(max_length=255)
    dimension_weights = models.JSONField(
        default=dict, 
        help_text="Mapping of Dimension IDs/Names to float values"
    )

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')


class QuestionaryResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'accounts.ClientProfile', 
        on_delete=models.PROTECT, 
        related_name="responses"
    )
    questionary = models.ForeignKey(Questionary, on_delete=models.CASCADE)
    selected_answers = models.JSONField(
        default=dict,
        help_text=_("Mapping of Question ID strings to selected Answer IDs")
    )
    scores_map = models.JSONField(
        default=dict,
        help_text=_("Calculated scores for each dimension at the time of completion")
    )
    is_filled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['client', 'questionary'])]
        verbose_name = _('Response')
        verbose_name_plural = _('Responses')

    def __str__(self):
        return str(self.id)


class QuestionaryScoreInterpretation(models.Model):
    questionary = models.ForeignKey(
        Questionary, 
        on_delete=models.CASCADE, 
        related_name="score_interpretations"
    )
    dimension = models.ForeignKey(QuestionaryDimension, on_delete=models.CASCADE)
    min_score = models.FloatField()
    max_score = models.FloatField()
    text = RichTextField()

    class Meta:
        verbose_name = _('Score Interpretation')
