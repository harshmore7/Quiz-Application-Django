from django.core.management.base import BaseCommand
from examapp.models import Subject, Question, Option, Student, Result, StudentAnswer
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # ------------------------
        # Subjects
        # ------------------------
        math, _ = Subject.objects.get_or_create(name="Mathematics")
        science, _ = Subject.objects.get_or_create(name="Science")

        # ------------------------
        # Questions
        # ------------------------
        q1, _ = Question.objects.get_or_create(
            qno=1,
            defaults={
                "question_text": "What is 2 + 2?",
                "subject": math
            }
        )

        q2, _ = Question.objects.get_or_create(
            qno=2,
            defaults={
                "question_text": "What is 10 / 2?",
                "subject": math
            }
        )

        q3, _ = Question.objects.get_or_create(
            qno=3,
            defaults={
                "question_text": "Water formula?",
                "subject": science
            }
        )

        # ------------------------
        # Options
        # ------------------------
        def create_options(question, options):
            for text, is_correct in options:
                Option.objects.get_or_create(
                    question=question,
                    text=text,
                    defaults={"is_correct": is_correct}
                )

        create_options(q1, [
            ("3", False),
            ("4", True),
            ("5", False),
            ("6", False),
        ])

        create_options(q2, [
            ("2", False),
            ("5", True),
            ("10", False),
            ("20", False),
        ])

        create_options(q3, [
            ("CO2", False),
            ("H2O", True),
            ("O2", False),
            ("NaCl", False),
        ])

        # ------------------------
        # User + Student
        # ------------------------
        user, created = User.objects.get_or_create(username="harsh")

        if created:
            user.set_password("1234")
            user.save()

        student, _ = Student.objects.get_or_create(
            user=user,
            defaults={"mobile": "9999999999"}
        )

        # ------------------------
        # Answers
        # ------------------------
        opt_correct = q1.options.filter(is_correct=True).first()

        StudentAnswer.objects.get_or_create(
            student=student,
            question=q1,
            defaults={"selected_option": opt_correct}
        )

        StudentAnswer.objects.get_or_create(
            student=student,
            question=q2,
            defaults={"selected_option": None}
        )

        # ------------------------
        # Result
        # ------------------------
        Result.objects.get_or_create(
            student=student,
            subject=math,
            defaults={"marks": 1, "total": 2}
        )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))