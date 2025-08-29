from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the custom user model

# Base model to include timestamps
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Course model
class Course(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})

# Enrollment model
class Enrollment(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

# Assessment model
class Assessment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    max_score = models.IntegerField()

# Submission model
class Submission(BaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    score = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

# Sponsor model
class Sponsor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'sponsor'})
    company_name = models.CharField(max_length=255, null=True, blank=True)
    funds_provided = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

# Sponsorship model
class Sponsorship(BaseModel):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('completed', 'Completed')])
    utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

# Notification model
class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)

# Email log model
class EmailLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    # Optional: You can remove this if created_at is enough
    sent_at = models.DateTimeField(auto_now_add=True)
