from django.contrib import admin
from django.utils.html import format_html
from .models import Project, BackgroundResearch, ResearchQuestions, Hypothesis


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_active", "updated_at", "document_link")
    list_filter = ("is_active",)
    search_fields = ("title", "owner__username", "owner__email")

    def document_link(self, obj):
        return format_html(
            '<a href="/planner/admin/document/{}/" target="_blank">View Document</a>', obj.id
        )


@admin.register(BackgroundResearch)
class BackgroundResearchAdmin(admin.ModelAdmin):
    list_display = ("project", "updated_at")
    search_fields = ("project__title", "topic", "key_terms")

@admin.register(ResearchQuestions)
class ResearchQuestionsAdmin(admin.ModelAdmin):
    list_display = ("project", "updated_at")
    search_fields = ("project__title", "final_question")

@admin.register(Hypothesis)
class HypothesisAdmin(admin.ModelAdmin):
    list_display = ("project", "updated_at")
    search_fields = ("project__title", "hypothesis")