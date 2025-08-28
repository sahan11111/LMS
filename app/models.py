from django.db import models
from  django.contrib.auth import get_user_model

User = get_user_model() # Get the custom user model

# Course model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})

# Enrollment model
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

#Assessment model
class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='course')
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    max_score = models.IntegerField()
# Submission model
class Submission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    score = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)