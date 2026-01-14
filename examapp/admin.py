from django.contrib import admin
from .models import Subject, Question, Option, Student, Result, StudentAnswer


# Admin Panel Customization
class OptionInline(admin.TabularInline):
    model = Option
    extra = 4   # shows 4 empty option rows by default


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('qno', 'question_text', 'subject')
    list_filter = ('subject',)
    inlines = [OptionInline]


# Register your models here.
admin.site.register(Subject)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(Student)
admin.site.register(Result)
admin.site.register(StudentAnswer)
