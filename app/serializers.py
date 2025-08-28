from rest_framework import serializers
from . import models
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
    
    def validate_created_by(self, value):
        if value.role != 'instructor':
            raise serializers.ValidationError("Only users with the instructor role can create courses.")
        return value