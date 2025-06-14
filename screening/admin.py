from django.contrib import admin
from screening.models import *
from screening.forms import TagScreeningAdminForm


@admin.register(TagScreening)
class TagScreeningAdmin(admin.ModelAdmin):
    form = TagScreeningAdminForm
    list_display = ('id', 'title', 'color')
    search_fields = ('title', 'color')
    ordering = ('title',)


@admin.register(QuestionaryCategory)
class QuestionaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(QuestionaryDimension)
class QuestionaryDimensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(QuestionaryDimensionValue)
class QuestionaryDimensionValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'dimension', 'value')
    list_filter = ('dimension',)
    search_fields = ('dimension__title',)
    ordering = ('dimension', 'value')


@admin.register(Questionary)
class QuestionaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_filter = ('categories', 'tags')
    search_fields = ('title',)
    ordering = ('title',)
    filter_horizontal = ('categories', 'tags')


@admin.register(QuestionaryScore)
class QuestionaryScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'questionary', 'dimension', 'min_score', 'max_score')
    list_filter = ('questionary', 'dimension')
    search_fields = ('title', 'questionary__title', 'dimension__title')
    ordering = ('questionary', 'dimension', 'title')


@admin.register(QuestionaryScoreExtra)
class QuestionaryScoreExtraAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'questionary')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')
    filter_horizontal = ('scores',)
    ordering = ('questionary', 'title')


@admin.register(QuestionaryQuestion)
class QuestionaryQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'questionary', 'weight')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')
    ordering = ('questionary', 'title')


@admin.register(QuestionaryAnswer)
class QuestionaryAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question')
    list_filter = ('question',)
    search_fields = ('title', 'question__title')
    filter_horizontal = ('values',)
    ordering = ('question', 'title')


@admin.register(QuestionaryResponse)
class QuestionaryResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'questionary', 'is_public', 'is_public_expert', 'created_at')
    list_filter = ('is_public', 'is_public_expert', 'questionary', 'created_at')
    search_fields = ('id', 'client__user__email', 'questionary__title')
    ordering = ('-created_at',)


@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    filter_horizontal = ('categories', 'tags')
    ordering = ('title',)


@admin.register(SurveyTheme)
class SurveyThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'survey')
    list_filter = ('survey',)
    search_fields = ('title', 'survey__title')
    ordering = ('survey', 'title')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'survey', 'completed_at')
    list_filter = ('survey', 'completed_at')
    search_fields = ('client__user__email', 'survey__title')
    ordering = ('-completed_at',)


@admin.register(SurveyEntry)
class SurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme', 'result', 'answer', 'created_at')
    list_filter = ('theme', 'result', 'created_at')
    search_fields = ('theme__title', 'result__client__user__email', 'answer')
    ordering = ('-created_at',)
