from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError

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
    
    def __str__(self):
        return self.title

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
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # percentage progress
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    
class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Lesson(BaseModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons',null=True,  blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.module.title})"

class LessonContent(BaseModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_contents', null=True, blank=True)
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50)  # pdf, video, text
    file = models.FileField(upload_to='lesson_contents/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.lesson.title})"

    
class Quiz(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    
    def __str__(self):
        return f"{self.title} ({self.course.title})"
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"
    
#  Student quiz submission models
class StudentSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    def __str__(self):
        return f"Submission by {self.student.username} for {self.quiz.title}"

class StudentAnswer(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)



# Assessment model
class Assessment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assessments', null=True, blank=True)
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    max_score = models.IntegerField()

    def __str__(self):
        return self.title
    
        
    def save(self, *args, **kwargs):  # FIXED: enforce validation
        self.full_clean()
        super().save(*args, **kwargs)


# Submission for modul model
class Submission(BaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    score = models.IntegerField(null=True, blank=True)
    content = models.TextField(blank=True, null=True)  #  Added for assignment-like responses
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} submitted {self.assessment.title}"

  # Validate if student is enrolled
    def clean(self):
        enrolled = Enrollment.objects.filter(
            student=self.student, course=self.assessment.course
        ).exists()
        if not enrolled:
            raise ValidationError("Student must be enrolled in the course to submit this assessment.")
        
    class Meta:
        unique_together = ("assessment", "student")  # one submission per assessment
        ordering = ["-submitted_at"]
# Sponsor model
class Sponsor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'sponsor'})
    company_name = models.CharField(max_length=255, null=True, blank=True)
    funds_provided = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return self.company_name or self.user.username

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
