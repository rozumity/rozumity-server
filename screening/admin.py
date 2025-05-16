from django.contrib import admin
from screening.models import *

# Register your models here.

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningCategory)
class ScreeningCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningDimension)
class ScreeningDimensionAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningQuestion)
class ScreeningQuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningAnswer)
class ScreeningAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningResponse)
class ScreeningResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningResult)
class ScreeningResultAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreeningResultInfo)
class ScreeningResultInfoAdmin(admin.ModelAdmin):
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
