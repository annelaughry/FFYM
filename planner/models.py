from django.conf import settings
from django.db import models

class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(max_length=200, default="Untitled Project")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} (by {self.owner})"


class GroupMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

class BackgroundResearch(models.Model):
    #First section of the student research planner.
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="background_research"
    )

    topic = models.CharField(
        max_length=300,
        help_text="What general topic does your research fall under?",
    )
    big_picture = models.TextField(
        blank=True,
        help_text="What is the global, national, or local issue related to your project? How does your project connect to environmental, technological, health, or sustainability challenges?",
    )
    prior_findings = models.TextField(
        blank=True,
        help_text="Summarize key studies, data, or findings from previous YSA projects and other credible sources."
    )
    key_terms = models.TextField(
        blank=True,
        help_text="List important scientific, technical, or environmental terms related to your project (comma-separated).",
    )
    term_definitions = models.TextField(
        blank=True,
        help_text= "Research definitions, processes, and how these concepts function in real-world applications.",
    )
    current_events = models.TextField(
        blank=True,
        help_text = "Look for news articles, scientific studies, or case studies related to your topic. Are there communities, schools, or organizations addressing similar issues?",
    )
    real_world = models.TextField(
        blank=True,
        help_text= "Why does this topic matter to your school, community, or the world? How can your project’s findings contribute to solving a problem or improving a situation?",
    )
    sources = models.TextField(
        blank=True,
        help_text="List links/citations you consulted (one per line)."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Background Research for {self.project}"

class ResearchQuestions(models.Model):
#Second section: scaffold students toward a clear, testable research question.
    project = models.OneToOneField(
    Project, on_delete=models.CASCADE, related_name="research_questions"
    )

    problem_statement = models.TextField(
    help_text="What problem are you trying to understand or solve? State it in 1–3 sentences."
    )
    question_brainstorm = models.TextField(
    help_text="Ask open-ended “how” and “why” questions about your general topic. List as many as possible, don’t limit yourself by thinking there is a “bad question",
    )
    so_what = models.TextField(
    help_text="Consider the “so what” of your topic. Why does this topic matter to you? Why should it matter to others?",
    )
    evaluate = models.TextField(
    help_text="Reflect on the questions you have considered. Identify one or two questions you find the most interesting and could be explored through research.",
    )
    final_question = models.TextField(
    help_text=" Enter your final research question(s). Keep the following questions in mind: What aspect of the more general topic will you explore? Is your research question clear? Is your research question focused? Is your research question complex enough to not be answered with a simple yes or no?",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"Research Questions for {self.project}"
    
class Hypothesis(models.Model):
    # Third section: scaffold students toward a testable hypothesis.
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="hypothesis"
    )
    hypothesis = models.TextField(
        help_text="Write your hypothesis below."
    )
    independent_variable = models.CharField(
        max_length=300,
        help_text="What variable are you in control of in this test?",
    )
    dependent_variable = models.CharField(
        max_length=300,
        help_text="What variable will you be measuring?",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hypothesis for {self.project}"

