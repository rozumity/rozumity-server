from django.contrib import admin
from screening.models import *
from screening.forms import TagScreeningAdminForm


@admin.register(TagScreening)
class TagScreeningAdmin(admin.ModelAdmin):
    form = TagScreeningAdminForm
    list_display = ('title', 'color', 'id')
    search_fields = ('title', 'color')
    ordering = ('title',)


@admin.register(CategoryScreening)
class CategoryScreeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(QuestionaryDimension)
class QuestionaryDimensionAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title',)
    ordering = ('title',)


#@admin.register(QuestionaryDimensionValue)
#class QuestionaryDimensionValueAdmin(admin.ModelAdmin):
#    list_display = ('id', 'dimension', 'answer', 'value')
#    list_filter = ('dimension', 'answer')
#    search_fields = ('dimension__title', 'answer__title')
#    ordering = ('dimension', 'answer', 'value')


@admin.register(Questionary)
class QuestionaryAdmin(admin.ModelAdmin):
    class QuestionaryCategoryInline(admin.TabularInline):
        model = Questionary.categories.through
        extra = 1
    class QuestionaryTagInline(admin.TabularInline):
        model = Questionary.tags.through
        extra = 1
    list_display = ('title', 'id')
    list_filter = ('categories', 'tags')
    search_fields = ('title',)
    ordering = ('title',)
    inlines = (QuestionaryCategoryInline, QuestionaryTagInline)
    exclude = ('categories', 'tags')


@admin.register(QuestionaryScore)
class QuestionaryScoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionary', 'dimension', 'min_score', 'max_score')
    list_filter = ('questionary', 'dimension')
    search_fields = ('title', 'questionary__title', 'dimension__title')
    ordering = ('questionary', 'dimension', 'title')


@admin.register(QuestionaryScoreExtra)
class QuestionaryScoreExtraAdmin(admin.ModelAdmin):
    class QuestionaryScoreInline(admin.TabularInline):
        model = QuestionaryScoreExtra.scores.through
        extra = 0
    list_display = ('title', 'questionary')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')
    ordering = ('questionary', 'title')
    inlines = (QuestionaryScoreInline,)
    exclude = ('scores',)


@admin.register(QuestionaryQuestion)
class QuestionaryQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'questionary', 'weight')
    list_filter = ('questionary',)
    search_fields = ('title', 'questionary__title')
    ordering = ('questionary', 'title')


@admin.register(QuestionaryAnswer)
class QuestionaryAnswerAdmin(admin.ModelAdmin):
    class QuestionaryDimensionValueInline(admin.TabularInline):
        model = QuestionaryAnswer.dimensions.through
        extra = 1
    list_display = ('title', 'question', 'question__questionary__title')
    list_filter = ('question',)
    search_fields = ('title', 'question__title', 'question__questionary__title')
    ordering = ('question', 'title')
    exclude = ('values',)
    inlines = (QuestionaryDimensionValueInline,)


@admin.register(QuestionaryResponse)
class QuestionaryResponseAdmin(admin.ModelAdmin):
    class QuestionaryAnswerInline(admin.TabularInline):
        model = QuestionaryResponse.answers.through
        extra, can_delete = 0, False
        def has_add_permission(self, request, obj=None):
            return False
        def has_change_permission(self, request, obj=None):
            return False
    class QuestionaryScoreInline(admin.TabularInline):
        model = QuestionaryResponse.scores.through
        extra, can_delete = 0, False
        def has_add_permission(self, request, obj=None):
            return False
        def has_change_permission(self, request, obj=None):
            return False
    class QuestionaryScoreExtraInline(admin.TabularInline):
        model = QuestionaryResponse.scores_extra.through
        extra, can_delete = 0, False
        def has_add_permission(self, request, obj=None):
            return False
        def has_change_permission(self, request, obj=None):
            return False
    list_display = ('client', 'questionary', 'is_public', 'is_public_expert', 'created_at')
    list_filter = ('is_public', 'is_public_expert', 'questionary', 'created_at')
    search_fields = ('id', 'client__user__email', 'questionary__title')
    ordering = ('-created_at',)
    inlines = (QuestionaryAnswerInline, QuestionaryScoreInline, QuestionaryScoreExtraInline)
    readonly_fields = ("scores_map",)

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title',)
    filter_horizontal = ('categories', 'tags')
    ordering = ('title',)


@admin.register(SurveyTheme)
class SurveyThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'survey', 'id')
    list_filter = ('survey',)
    search_fields = ('title', 'survey__title')
    ordering = ('survey', 'title')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ('client', 'survey', 'completed_at', 'id')
    list_filter = ('survey', 'completed_at')
    search_fields = ('client__user__email', 'survey__title')
    ordering = ('-completed_at',)


@admin.register(SurveyEntry)
class SurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('theme', 'result', 'answer', 'created_at', 'id')
    list_filter = ('theme', 'result', 'created_at')
    search_fields = ('theme__title', 'result__client__user__email', 'answer')
    ordering = ('-created_at',)
