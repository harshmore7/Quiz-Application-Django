from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from .models import Result, Student, Question, Subject, Option, StudentAnswer
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import make_aware


# ------------------------
# BASIC VIEWS
# ------------------------

def home(request):
    return render(request, 'examapp/home.html')


def register_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']

        if User.objects.filter(username=username).exists():
            return render(request, 'examapp/register.html', {
                'error': 'Username already taken.'
            })

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            Student.objects.create(user=user, mobile=mobile)
            return redirect('login')
        except Exception:
            return render(request, 'examapp/register.html', {
                'error': 'Registration failed.'
            })

    return render(request, 'examapp/register.html')


def login_student(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'examapp/login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'examapp/login.html')


def logout_student(request):
    logout(request)
    return redirect('login')


# ------------------------
# STAFF CHECK
# ------------------------

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        return view_func(request, *args, **kwargs)
    return wrapper


# ------------------------
# QUESTION MANAGEMENT
# ------------------------

@login_required
@staff_required
def question_list(request):
    subject_filter = request.GET.get('subject')
    questions = Question.objects.all()

    if subject_filter:
        questions = questions.filter(subject__name=subject_filter)

    subjects = Subject.objects.all()

    return render(request, 'examapp/questions/list.html', {
        'questions': questions,
        'subjects': subjects,
        'selected_subject': subject_filter
    })


@login_required
@staff_required
def add_question(request):
    subjects = Subject.objects.all()

    if request.method == "POST":
        question = Question.objects.create(
            qno=request.POST['qno'],
            question_text=request.POST['question_text'],
            subject_id=request.POST['subject']
        )

        options = request.POST.getlist('option')
        correct = request.POST.get('correct')

        for i, text in enumerate(options):
            Option.objects.create(
                question=question,
                text=text,
                is_correct=(str(i) == correct)
            )

        return redirect('question_list')

    return render(request, 'examapp/questions/add.html', {'subjects': subjects})


@login_required
@staff_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    subjects = Subject.objects.all()

    if request.method == "POST":
        question.qno = request.POST['qno']
        question.question_text = request.POST['question_text']
        question.subject_id = request.POST['subject']
        question.save()

        question.options.all().delete()

        options = request.POST.getlist('option')
        correct = request.POST.get('correct')

        for i, text in enumerate(options):
            if text.strip():
                Option.objects.create(
                    question=question,
                    text=text,
                    is_correct=(str(i) == correct)
                )

        return redirect('question_list')

    return render(request, 'examapp/questions/edit.html', {
        'question': question,
        'subjects': subjects
    })


@login_required
@staff_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == "POST":
        question.delete()
        return redirect('question_list')

    return render(request, 'examapp/questions/delete.html', {
        'question': question
    })


# ------------------------
# TEST FLOW
# ------------------------

@login_required
def start_test(request):
    if request.user.is_superuser:
        return render(request, "examapp/message.html", {
            "message": "Only students can start tests."
        })

    try:
        student = request.user.student
    except:
        return render(request, "examapp/message.html", {
            "message": "Student profile not found."
        })

    subjects = Subject.objects.all()

    attempted_subjects = Result.objects.filter(
        student=student
    ).values_list("subject_id", flat=True)

    return render(request, "examapp/start_test.html", {
        "subjects": subjects,
        "attempted_subjects": attempted_subjects
    })


@login_required
def start_subject_test(request, subject_id):
    request.session.pop("answers", None)

    start_time = timezone.now()
    end_time = start_time + timedelta(minutes=10)

    request.session["test_start_time"] = start_time.isoformat()
    request.session["test_end_time"] = end_time.isoformat()

    return redirect("test_question", subject_id=subject_id, q_index=0)


@login_required
def test_question(request, subject_id, q_index):
    student = request.user.student
    subject = Subject.objects.get(id=subject_id)
    questions = list(Question.objects.filter(subject=subject))

    if q_index >= len(questions):
        return redirect("end_test", subject_id)

    question = questions[q_index]

    end_time = datetime.fromisoformat(request.session["test_end_time"])
    if end_time.tzinfo is None:
        end_time = make_aware(end_time)

    remaining_seconds = int((end_time - timezone.now()).total_seconds())

    if remaining_seconds <= 0:
        return redirect("end_test", subject_id)

    if request.method == "POST":
        selected_option_id = request.POST.get("option")

        if selected_option_id:
            StudentAnswer.objects.update_or_create(
                student=student,
                question=question,
                defaults={"selected_option_id": selected_option_id}
            )

        if "prev" in request.POST and q_index > 0:
            return redirect("test_question", subject_id, q_index - 1)

        if "next" in request.POST:
            return redirect("test_question", subject_id, q_index + 1)

        if "finish" in request.POST:
            return redirect("end_test", subject_id)

    selected_answer = StudentAnswer.objects.filter(
        student=student,
        question=question
    ).first()

    return render(request, "examapp/test_question.html", {
        "question": question,
        "q_index": q_index,
        "total": len(questions),
        "remaining_seconds": remaining_seconds,
        "subject_id": subject.id,
        "questions": questions,
        "selected_answer": selected_answer,
    })


@login_required
def end_test(request, subject_id):
    student = request.user.student
    questions = Question.objects.filter(subject_id=subject_id)

    score = 0
    for q in questions:
        try:
            answer = StudentAnswer.objects.get(student=student, question=q)
            if answer.selected_option and answer.selected_option.is_correct:
                score += 1
        except StudentAnswer.DoesNotExist:
            pass

    Result.objects.get_or_create(
        student=student,
        subject_id=subject_id,
        defaults={'marks': score, 'total': questions.count()}
    )

    return render(request, 'examapp/result.html', {
        'score': score,
        'total': questions.count()
    })


@login_required
def result_list(request):
    student = request.user.student
    results = Result.objects.filter(student=student).order_by('-date')

    return render(request, 'examapp/results.html', {
        'results': results
    })


# ------------------------
# PROFILE
# ------------------------

@login_required
def profile_view(request):
    return render(request, 'examapp/profile/view.html', {
        'student': request.user.student
    })


@login_required
def profile_edit(request):
    student = request.user.student
    user = request.user

    if request.method == "POST":
        user.username = request.POST['username']
        user.email = request.POST['email']
        student.mobile = request.POST['mobile']

        user.save()
        student.save()

        return redirect('profile')

    return render(request, 'examapp/profile/edit.html', {
        'student': student
    })


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('profile')

    return render(request, 'examapp/profile/change_password.html', {
        'form': form
    })


# ------------------------
# STUDENT MANAGEMENT (STAFF)
# ------------------------

@login_required
@staff_required
def student_list(request):
    students = Student.objects.select_related('user')
    return render(request, 'examapp/students/list.html', {
        'students': students
    })


@login_required
@staff_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student)

    return render(request, 'examapp/students/detail.html', {
        'student': student,
        'results': results
    })


@login_required
@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        student.user.delete()
        return redirect('student_list')

    return render(request, 'examapp/students/delete.html', {
        'student': student
    })