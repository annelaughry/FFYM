from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import formset_factory
from django.db import transaction
from .models import Classroom, Membership, Assignment, Question, StudentResponse, Feedback
from .forms import ResponseForm, FeedbackForm, UserRegisterForm, ClassroomForm, AssignmentForm, QuestionFormSet
from django.contrib.auth import login
from django.http import HttpResponseForbidden
import random, string
from django.db.models import Count
from django.contrib.auth import get_user_model

User = get_user_model()


def is_teacher(user, classroom):
    return Membership.objects.filter(user=user, classroom=classroom, role='teacher').exists()


@login_required
def dashboard(request):
    mships = Membership.objects.filter(user=request.user)
    classrooms = [m.classroom for m in mships]
    student_assignments = Assignment.objects.filter(classroom__in=classrooms, published=True)
    return render(request, 'core/dashboard.html', {'assignments': student_assignments, 'classrooms': classrooms})


@login_required
def join_classroom(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        classroom = get_object_or_404(Classroom, code=code)
        Membership.objects.get_or_create(user=request.user, classroom=classroom, defaults={'role': 'student'})
        return redirect('dashboard')
    return render(request, 'core/join_classroom.html')

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, published=True)
    questions = list(assignment.questions.all())
    existing = {
        r.question_id: r
        for r in StudentResponse.objects.filter(assignment=assignment, student=request.user)
    }
    initial = [{'answer': existing.get(q.id).answer if existing.get(q.id) else ''} for q in questions]
    ResponseFormSet = formset_factory(ResponseForm, extra=0)
    formset = ResponseFormSet(initial=initial)
    pairs = list(zip(questions, formset.forms))
    return render(request, 'core/assignment_detail.html', {
        'assignment': assignment,
        'formset': formset,
        'pairs': pairs,
    })


@login_required
@transaction.atomic
def submit_responses(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, published=True)
    questions = list(assignment.questions.all())
    ResponseFormSet = formset_factory(ResponseForm, extra=0)
    if request.method == 'POST':
        formset = ResponseFormSet(request.POST)
        if formset.is_valid():
            for form, question in zip(formset, questions):
                obj, created = StudentResponse.objects.get_or_create(
                    assignment=assignment, question=question, student=request.user,
                    defaults={'answer': form.cleaned_data.get('answer', '')}
                )
                if not created:
                    obj.answer = form.cleaned_data.get('answer', '')
                    obj.save()
            return redirect('assignment_submitted', pk=assignment.pk)
    return redirect('assignment_detail', pk=assignment.pk)

@login_required
def assignment_submitted(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'core/assignment_submitted.html', {'assignment': assignment})

# Teacher views
@login_required
def teacher_classroom(request, class_id):
    classroom = get_object_or_404(Classroom, pk=class_id)
    if not is_teacher(request.user, classroom) and request.user != classroom.owner:
        return redirect('dashboard')

    # Students enrolled in this classroom
    students = (Membership.objects
                .filter(classroom=classroom, role='student')
                .select_related('user')
                .order_by('user__last_name', 'user__first_name', 'user__username'))

    # Assignments with number of distinct student submitters
    assignments = (classroom.assignments
                .annotate(submitters=Count('responses__student', distinct=True))
                .order_by('-due_at', 'title'))


    total_students = students.count()


    return render(request, 'core/teacher_classroom.html', {
        'classroom': classroom,
        'assignments': assignments,
        'students': students,
        'total_students': total_students,
})

@login_required
def teacher_assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if not is_teacher(request.user, assignment.classroom) and request.user != assignment.classroom.owner:
        return redirect('dashboard')
    # Group responses by student
    responses = (StudentResponse.objects
            .filter(assignment=assignment)
            .select_related('student','question')
            .order_by('student__username','question__order'))
    # Build nested structure: {student: [(question, response, feedback), ...]}
    data = {}
    for r in responses:
        fb = getattr(r, 'feedback', None)
        data.setdefault(r.student, []).append((r.question, r, fb))
    return render(request, 'core/teacher_assignment_detail.html', {'assignment': assignment, 'data': data})


@login_required
def review_response(request, resp_id):
    resp = get_object_or_404(StudentResponse, pk=resp_id)
    classroom = resp.assignment.classroom
    if not is_teacher(request.user, classroom) and request.user != classroom.owner:
        return redirect('dashboard')
    fb = getattr(resp, 'feedback', None)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=fb)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.response = resp
            feedback.teacher = request.user
            feedback.save()
            return redirect('teacher_assignment_detail', pk=resp.assignment.pk)
    else:
        form = FeedbackForm(instance=fb)
    return render(request, 'core/review_response.html', {'resp': resp, 'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']

            # Optional: auto-create a default classroom for teachers
            if role == 'teacher':
                classroom = Classroom.objects.create(
                    name=f"{user.username}'s Classroom",
                    code=user.username[:4].upper() + '1234',  # simple placeholder
                    owner=user
                )
                Membership.objects.create(user=user, classroom=classroom, role='teacher')
            else:
                # Students will join classrooms later via a code
                pass

            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def _rand_code(n=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

@login_required
def my_classrooms(request):
    """Classes I own or where I'm a teacher."""
    owned = Classroom.objects.filter(owner=request.user)
    teaching_ids = Membership.objects.filter(user=request.user, role='teacher').values_list('classroom_id', flat=True)
    teaching = Classroom.objects.filter(id__in=teaching_ids).exclude(owner=request.user)
    return render(request, 'core/teacher_classrooms_list.html', {"owned": owned, "teaching": teaching})

@login_required
def create_classroom(request):
    """Teachers can create a new classroom; sets owner and adds teacher membership."""
    # Only allow if user is a teacher somewhere OR choose to allow anyone to create
    # Simpler policy: anyone can create; owner implies teacher.
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            # Auto-generate code if left blank
            if not classroom.code:
                base = _rand_code()
                while Classroom.objects.filter(code=base).exists():
                    base = _rand_code()
                classroom.code = base
            classroom.owner = request.user
            classroom.save()
            Membership.objects.get_or_create(user=request.user, classroom=classroom, role='teacher')
            return redirect('teacher_classroom', class_id=classroom.id)
    else:
        form = ClassroomForm()
    return render(request, 'core/classroom_form.html', {"form": form})

@login_required
def create_assignment(request, class_id):
    classroom = get_object_or_404(Classroom, pk=class_id)
    if not is_teacher(request.user, classroom) and request.user != classroom.owner:
        return redirect('dashboard')

    assignment = Assignment(classroom=classroom)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        formset = QuestionFormSet(request.POST, instance=assignment)
        if form.is_valid() and formset.is_valid():
            assignment = form.save()
            formset.instance = assignment
            formset.save()
            return redirect('teacher_classroom', class_id=classroom.id)
    else:
        form = AssignmentForm(instance=assignment)
        formset = QuestionFormSet(instance=assignment)

    return render(request, 'core/assignment_form.html', {
        'form': form, 'formset': formset, 'classroom': classroom
    })

@login_required
def edit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    if not is_teacher(request.user, classroom) and request.user != classroom.owner:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        formset = QuestionFormSet(request.POST, instance=assignment)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('teacher_classroom', class_id=classroom.id)
    else:
        form = AssignmentForm(instance=assignment)
        formset = QuestionFormSet(instance=assignment)

    return render(request, 'core/assignment_form.html', {
        'form': form, 'formset': formset, 'classroom': classroom, 'assignment': assignment
    })
