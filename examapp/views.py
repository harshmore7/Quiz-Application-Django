from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import Student, Question, Subject, Option

# Create your views here.
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
            return redirect('question_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_student(request):
    logout(request)
    return redirect('login')

# Logic for question listing, adding, editing, deleting
@login_required
def question_list(request):
    questions = Question.objects.all()
    return render(request, 'questions/list.html', {'questions': questions})


@login_required
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
def delete_question(request, pk):
    question = Question.objects.get(pk=pk)

    if request.method == "POST":
        question.delete()
        return redirect('question_list')

    return render(request, 'questions/delete.html', {'question': question})
