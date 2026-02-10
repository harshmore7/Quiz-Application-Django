from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import Result, Student, Question, Subject, Option, StudentAnswer
from datetime import timedelta
from django.utils import timezone
from datetime import datetime

# Create your views here.
def home(request):
    return render(request, 'home.html')

def register_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']

        user = User.objects.create_user(
            username = username,
            email = email,
            password = password
        )

        Student.objects.create(
            user = user,
            mobile = mobile
        )

        return redirect('login')
    return render(request, 'register.html')

def login_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_student(request):
    logout(request)
    return redirect('login')

# decorator to check staff status
def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


# Logic for question listing, adding, editing, deleting
@login_required
@staff_required
def question_list(request):
    subject_filter = request.GET.get('subject')

    questions = Question.objects.all()

    if subject_filter:
        questions = questions.filter(subject__name=subject_filter)

    subjects = Subject.objects.all()

    return render(request, 'questions/list.html', {
        'questions': questions,
        'subjects': subjects,
        'selected_subject': subject_filter
    })


@login_required
@staff_required
def add_question(request):
    subjects = Subject.objects.all()

    if request.method == "POST":
        qno = request.POST['qno']
        question_text = request.POST['question_text']
        subject_id = request.POST['subject']

        question = Question.objects.create(
            qno=qno,
            question_text=question_text,
            subject_id=subject_id
        )

        options = request.POST.getlist('option')
        correct = request.POST.get('correct')

        for index, text in enumerate(options):
            Option.objects.create(
                question=question,
                text=text,
                is_correct=(str(index) == correct)
            )

        return redirect('question_list')

    return render(request, 'questions/add.html', {'subjects': subjects})


@login_required
@staff_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    subjects = Subject.objects.all()

    if request.method == "POST":
        # update question fields
        question.qno = request.POST['qno']
        question.question_text = request.POST['question_text']
        question.subject_id = request.POST['subject']
        question.save()

        # remove old options
        question.options.all().delete()

        # add updated options
        options = request.POST.getlist('option')
        correct = request.POST.get('correct')

        for index, text in enumerate(options):
            if text.strip():  # avoid empty options
                Option.objects.create(
                    question=question,
                    text=text,
                    is_correct=(str(index) == correct)
                )

        return redirect('question_list')

    return render(request, 'questions/edit.html', {
        'question': question,
        'subjects': subjects
    })



@login_required
@staff_required
def delete_question(request, pk):
    question = Question.objects.get(pk=pk)

    if request.method == "POST":
        question.delete()
        return redirect('question_list')

    return render(request, 'questions/delete.html', {'question': question})

@login_required
def start_test(request):
    # ❌ admins should not start tests
    if request.user.is_superuser:
        return render(request, "message.html", {
            "message": "Only students can start tests."
        })

    student = request.user.student

    # show subject list
    if request.method == "GET":
        subjects = Subject.objects.all()
        attempted_subjects = Result.objects.filter(
            student=student
        ).values_list("subject_id", flat=True)

        return render(request, "start_test.html", {
            "subjects": subjects,
            "attempted_subjects": attempted_subjects
        })
    
@login_required
def start_subject_test(request, subject_id):
    if request.user.is_superuser:
        return render(request, "message.html", {
            "message": "Only students can start tests."
        })

    # clear old test data
    request.session.pop("answers", None)

    # ⏱️ set test time (10 minutes)
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
    question = questions[q_index]

    # ⏱ timer (keep as-is)
    end_time = datetime.fromisoformat(request.session["test_end_time"])
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

        # ⬅️ PREVIOUS
        if "prev" in request.POST and q_index > 0:
            return redirect("test_question", subject_id, q_index - 1)

        # ➡️ NEXT
        if "next" in request.POST and q_index < len(questions) - 1:
            return redirect("test_question", subject_id, q_index + 1)

        # ✅ FINISH
        if "finish" in request.POST:
            return redirect("end_test", subject_id)

    # 🔍 Get answered question IDs for this student & subject
    answered_q_ids = set(
        StudentAnswer.objects.filter(
            student=student,
            question__subject=subject,
            selected_option__isnull=False   # ⭐ THIS IS THE FIX
        ).values_list("question_id", flat=True)
    )


    return render(request, "test_question.html", {
        "question": question,
        "q_index": q_index,
        "total": len(questions),
        "remaining_seconds": remaining_seconds,
        "subject_id": subject.id,
        "questions": questions,
        "answered_q_ids": answered_q_ids, 
    })



@login_required
def end_test(request, subject_id):
    student = request.user.student
    questions = Question.objects.filter(subject_id=subject_id)

    score = 0
    for q in questions:
        try:
            answer = StudentAnswer.objects.get(student=student, question=q)
            if answer.selected_option.is_correct:
                score += 1
        except StudentAnswer.DoesNotExist:
            pass

    Result.objects.create(
        student=student,
        subject_id=subject_id,
        marks=score,
        total=questions.count()
    )

    return render(request, 'result.html', {
        'score': score,
        'total': questions.count()
    })


    

@login_required
def result_list(request):
    student = request.user.student
    results = Result.objects.filter(student=student).order_by('-date')

    return render(request, 'results.html', {
        'results': results
    })


# Staff views for student management
@login_required
@staff_required
def student_list(request):
    students = Student.objects.select_related('user')
    return render(request, 'students/list.html', {
        'students': students
    })

@login_required
@staff_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student)

    return render(request, 'students/detail.html', {
        'student': student,
        'results': results
    })

@login_required
@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        student.user.delete()  # deletes user + student (cascade)
        return redirect('student_list')

    return render(request, 'students/delete.html', {
        'student': student
    })

# Profile management views 

@login_required
def profile_view(request):
    student = request.user.student
    return render(request, 'profile/view.html', {
        'student': student
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

    return render(request, 'profile/edit.html', {
        'student': student
    })

# Change password view
@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # VERY IMPORTANT
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'profile/change_password.html', {
        'form': form
    })
