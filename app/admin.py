from django.contrib import admin
from .models import *

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by')  # Removed 'created' or 'created_at'
    search_fields = ('title', 'created_by__username')
    ordering = ('id',)
    list_per_page = 10


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'status', 'progress')  
    search_fields = ('student__username', 'course__title')
    # Removed list_filter for 'created'
    ordering = ('id',)
    list_per_page = 10


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'due_date')
    search_fields = ('title', 'course__title')
    list_filter = ('due_date',)
    ordering = ('id',)
    list_per_page = 10


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assessment', 'student', 'submitted_at', 'score')  # changed 'grade' to 'score'
    search_fields = ('assessment__title', 'student__username')
    list_filter = ('submitted_at', 'score')  # 'score' is a field, so this works
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
    # list_filter = ('status', 'created_at')
    ordering = ('id',)
    list_per_page = 10
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):  
    list_display = ('id', 'user', 'type', 'is_read', 'created_at')
    search_fields = ('user__username', 'type', 'message')
    # list_filter = ('is_read', 'type', 'created_at')
    ordering = ('id',)
    list_per_page = 10
@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):  
    list_display = ('id', 'user', 'subject', 'sent_at')
    search_fields = ('user__username', 'subject' )
    # list_filter = ('status', 'sent_at')
    ordering = ('id',)
    list_per_page = 10
