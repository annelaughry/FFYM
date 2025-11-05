from django.urls import path
from . import views

app_name = "planner"  

urlpatterns = [
    path('', views.home, name='home'), 
    path("start/", views.start_project, name="start_project"),
    path("background-research/", views.background_research_edit, name="background_research_edit"),
    path("admin/document/<int:project_id>/", views.project_document_view, name="project_document_view"),
    path("research-questions/", views.research_questions_edit, name="research_questions_edit"),
    path("hypothesis/", views.hypothesis_edit, name="hypothesis_edit"),

]

