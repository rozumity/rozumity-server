from django.contrib import admin
from screening.models import *
from screening.forms import TagScreeningAdminForm

# Register your models here.

@admin.register(TagScreening)
class TagScreeningAdmin(admin.ModelAdmin):
    form = TagScreeningAdminForm
    list_filter = ()
    list_display = ('title', 'color', 'id')
    search_fields = ('title', 'color')


@admin.register(Questionary)
class QuestionaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    list_filter = ('categories', 'tags')
    search_fields = ('title',)


@admin.register(CategoryQuestionary)
class CategoryQuestionaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    list_filter = ()
    search_fields = ('title',)


@admin.register(QuestionaryDimension)
class QuestionaryDimensionAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    list_filter = ()
    search_fields = ('title',)


@admin.register(QuestionaryScore)
class QuestionaryScoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension', 'min_score', 'max_score')
    list_filter = ('dimension',)
    search_fields = ('title', 'dimension__title')


@admin.register(QuestionaryQuestion)
class QuestionaryQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionary', 'weight')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')


@admin.register(QuestionaryAnswerValue)
class QuestionaryAnswerValueAdmin(admin.ModelAdmin):
    list_display = ('dimension', 'value')
    list_filter = ('dimension',)
    search_fields = ('dimension__title',)


@admin.register(QuestionaryAnswer)
class QuestionaryAnswerAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')
    list_filter = ('question',)
    search_fields = ('title', 'question__title')


@admin.register(QuestionaryResponse)
class QuestionaryResponseAdmin(admin.ModelAdmin):
    list_display = ('client', 'questionary', 'is_public', 'is_public_expert', 'created_at')
    list_filter = ('is_public', 'is_public_expert', 'questionary', 'created_at')
    search_fields = ('id', 'questionary__title', 'result__title')


@admin.register(QuestionaryResult)
class QuestionaryResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionary', 'id')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)
    list_filter = ()
    search_fields = ('title',)


@admin.register(CategorySurvey)
class CategorySurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    list_filter = ()
    search_fields = ('title',)


@admin.register(SurveyTheme)
class SurveyThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'survey')
    list_filter = ('survey',)
    search_fields = ('title', 'survey__title')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'survey', 'completed_at')
    list_filter = ('survey', 'completed_at')
    search_fields = ('client__client_id', 'survey__title')


@admin.register(SurveyEntry)
class SurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme', 'result', 'answer', 'created_at')
    list_filter = ('theme', 'result', 'created_at')
    search_fields = ('theme__title', 'result__client__client_id', 'answer')
