from django.contrib import admin
from screening.models import *

# Register your models here.

@admin.register(Questionary)
class QuestionaryAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryCategory)
class QuestionaryCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryDimension)
class QuestionaryDimensionAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryQuestion)
class QuestionaryQuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryAnswer)
class QuestionaryAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryResponse)
class QuestionaryResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionaryResult)
class QuestionaryResultAdmin(admin.ModelAdmin):
    pass


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    pass


@admin.register(SurveyTheme)
class SurveyThemeAdmin(admin.ModelAdmin):
    pass


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    pass


@admin.register(SurveyEntry)
class SurveyEntryAdmin(admin.ModelAdmin):
    pass
