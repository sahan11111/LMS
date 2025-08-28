from rest_framework import serializers
from . import models
from core.serializers import UserSerializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
    
    def validate_created_by(self, value):
        if value.role != 'instructor':
            raise serializers.ValidationError("Only users with the instructor role can create courses.")
        return value
    
    
class EnrollmentSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = models.Enrollment
        fields = ['id', 'student', 'course', 'status', 'progress']

    def validate(self, data):
        user = self.context['request'].user
        if user.role != 'student':
            raise serializers.ValidationError("Only students can enroll in courses.")
        return data

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

    
    
class AssessmentSerializer(serializers.ModelSerializer):
    # course = CourseSerializer(read_only=True)
    class Meta:
        model = models.Assessment
        fields = ['id', 'course', 'title', 'due_date', 'max_score']
        
    
class SubmissionSerializer(serializers.ModelSerializer):
    # student = UserSerializer(read_only=True)
    # assessment = AssessmentSerializer(read_only=True)
    class Meta:
        model = models.Submission
        fields = ['id', 'assessment', 'student', 'score', 'submitted_at']
    
    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError("Only users with the student role can submit assessments.")
        return value