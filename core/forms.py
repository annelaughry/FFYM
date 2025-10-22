from django import forms
from django.contrib.auth.models import User
from django.forms import modelform_factory, inlineformset_factory
from .models import StudentResponse, Feedback, Membership, Classroom, Assignment, Question


ResponseForm = modelform_factory(StudentResponse, fields=['answer'])


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment','score']

class UserRegisterForm(forms.ModelForm):
    ROLE_CHOICES = [('student', 'Student'), ('teacher', 'Teacher')]
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ["name", "code"] # allow manual code entry OR auto-fill in view
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g., Period 2 Biology"}),
            "code": forms.TextInput(attrs={"placeholder": "e.g., BIO2A7"}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'link', 'instructions', 'due_at', 'published']
        widgets = {
            'due_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com/reading'}),
        }

QuestionFormSet = inlineformset_factory(
    Assignment, Question,
    fields=['prompt', 'order'],
    extra=3,           # show 3 blanks by default
    can_delete=True
)
