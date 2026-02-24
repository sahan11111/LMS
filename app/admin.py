from django.contrib import admin
from .models import (
    Course, Enrollment, Assessment, Submission, Sponsor, Sponsorship,
    Notification, EmailLog, Module, Lesson, LessonContent, Quiz, Question, Answer,
    StudentSubmission, StudentAnswer,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty_level', 'created_by', 'created_at')
    search_fields = ('title', 'created_by__username')
    list_filter = ('difficulty_level',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'status', 'progress', 'created_at')
    search_fields = ('student__username', 'course__title')
    list_filter = ('status',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'due_date', 'max_score')
    search_fields = ('title', 'course__title')
    list_filter = ('due_date',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assessment', 'student', 'submitted_at', 'score')
    search_fields = ('assessment__title', 'student__username')
    list_filter = ('submitted_at',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company_name', 'funds_provided')
    search_fields = ('user__username', 'company_name')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'student', 'amount', 'status', 'utilization', 'created_at')
    search_fields = ('sponsor__user__username', 'student__username', 'status')
    list_filter = ('status',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'is_read', 'created_at')
    search_fields = ('user__username', 'type', 'message')
    list_filter = ('is_read', 'type')
    ordering = ('id',)
    list_per_page = 10


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'created_at')
    search_fields = ('user__username', 'subject')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'created_by', 'created_at', 'updated_at')
    search_fields = ('course__title', 'title')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'module', 'title', 'created_at', 'updated_at')
    search_fields = ('module__title', 'title')
    ordering = ('id',)
    list_per_page = 10


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'content_type', 'created_at', 'updated_at')
    search_fields = ('lesson__title', 'content_type')
    list_filter = ('content_type',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'created_by', 'created_at')
    search_fields = ('title', 'course__title')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text')
    search_fields = ('text', 'quiz__title')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    search_fields = ('text',)
    list_filter = ('is_correct',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'quiz', 'score', 'percentage', 'passed', 'submitted_at')
    search_fields = ('student__username', 'quiz__title')
    list_filter = ('passed',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'question', 'selected_answer')
    ordering = ('id',)
    list_per_page = 10