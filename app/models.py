from django.db import models
from  django.contrib.auth import get_user_model

User = get_user_model() # Get the custom user model

# Course model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    
