from django.db import models
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL


class Classroom(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=12, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_classrooms')
    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = (('teacher','Teacher'), ('student','Student'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    class Meta:
        unique_together = ('user','classroom')


class Article(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    body = models.TextField(blank=True)
    def __str__(self):
        return self.title

class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True)  # temporarily optional
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    link = models.URLField(blank=True)  # ← NEW, not required
    due_at = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} ({self.classroom})"
    
class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    prompt = models.TextField()
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order','id']
    def __str__(self):
        return self.prompt[:50]
    
class StudentResponse(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ('assignment','question','student')

class Feedback(models.Model):
    response = models.OneToOneField(StudentResponse, on_delete=models.CASCADE, related_name='feedback')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedback')
    comment = models.TextField(blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)