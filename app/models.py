from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class BaseModel(models.Model):
    """Base model with timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'},
        related_name='courses'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


class Enrollment(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['id']

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'},
        related_name='modules'
    )

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    class Meta:
        ordering = ['id']


class Lesson(BaseModel):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        related_name='lessons',
        null=True, blank=True
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        module_title = self.module.title if self.module else 'No Module'
        return f"{self.title} ({module_title})"

    class Meta:
        ordering = ['id']


class LessonContent(BaseModel):
    CONTENT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('text', 'Text'),
    ]
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='lesson_contents',
        null=True, blank=True
    )
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    file = models.FileField(upload_to='lesson_contents/', null=True, blank=True)

    def __str__(self):
        lesson_title = self.lesson.title if self.lesson else 'No Lesson'
        return f"{self.title} ({lesson_title})"

    class Meta:
        ordering = ['id']


class Quiz(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'},
        related_name='quizzes'
    )

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['id']

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


class StudentSubmission(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='quiz_submissions'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'quiz')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.student.username} for {self.quiz.title}"


class StudentAnswer(models.Model):
    submission = models.ForeignKey(
        StudentSubmission, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='student_answers'
    )
    selected_answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Answer to '{self.question.text}'"


class Assessment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        related_name='assessments',
        null=True, blank=True
    )
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    max_score = models.IntegerField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Submission(BaseModel):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='assessment_submissions'
    )
    score = models.IntegerField(null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assessment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} submitted {self.assessment.title}"

    def clean(self):
        """Validate that student is enrolled in the course."""
        enrolled = Enrollment.objects.filter(
            student=self.student, course=self.assessment.course
        ).exists()
        if not enrolled:
            raise ValidationError(
                'Student must be enrolled in the course to submit this assessment.'
            )


class Sponsor(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'sponsor'},
        related_name='sponsor_profile'
    )
    company_name = models.CharField(max_length=255, null=True, blank=True)
    funds_provided = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.company_name or self.user.username

    class Meta:
        ordering = ['id']


class Sponsorship(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name='sponsorships')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='sponsorships'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.sponsor} -> {self.student.username} ({self.status})"


class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('enrollment', 'Enrollment'),
        ('sponsorship', 'Sponsorship'),
        ('assessment', 'Assessment'),
        ('general', 'General'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


class EmailLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    subject = models.CharField(max_length=255)
    body = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.user.username}: {self.subject}"