from django.contrib import admin
from .models import Classroom, Membership, Article, Assignment, Question, StudentResponse, Feedback


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title','classroom','article','instructions','published','due_at')
    list_filter = ('classroom','published')
    inlines = [QuestionInline]


admin.site.register([Classroom, Membership, Article, StudentResponse, Feedback])