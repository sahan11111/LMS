from rest_framework import serializers
from . import models
from core.serializers import UserSerializer
from rest_framework import serializers
from . import models  # assuming your Course model is in models.py

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
    
    #get_fields is used to make created_by read_only for non-admins
    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.groups.filter(name="Admin").exists():
            fields['created_by'].read_only = True
        return fields

    def validate_created_by(self, value):
        user = self.context['request'].user

        if user.groups.filter(name="Admin").exists():
            # Admins can set created_by freely
            return value

        elif user.groups.filter(name="Instructor").exists():
            # Instructors can only set created_by to themselves
            if value != user:
                raise serializers.ValidationError("Instructors can only assign themselves as the course creator.")
            return value

        raise serializers.ValidationError("You are not allowed to create courses.")

    def create(self, validated_data):
        user = self.context['request'].user

        # If created_by isn't explicitly provided, set it to the current user
        if 'created_by' not in validated_data:
            validated_data['created_by'] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Prevent instructors or non-admins from changing created_by
        if 'created_by' in validated_data:
            if not user.groups.filter(name="Admin").exists():
                validated_data.pop('created_by', None)

        return super().update(instance, validated_data)

    
    
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
    class Meta:
        model = models.Assessment
        fields = ['id', 'course', 'title', 'due_date', 'max_score']

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user

        # Make 'course' read-only for users who are not Admin or Instructor
        if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
            fields['course'].read_only = True
        
        return fields

    def validate_course(self, value):
        user = self.context['request'].user

        # Admin can assign any course
        if user.groups.filter(name="Admin").exists():
            return value
        
        # Instructors can only assign courses they created
        if user.groups.filter(name="Instructor").exists():
            if value.created_by != user:
                raise serializers.ValidationError("You can only assign assessments to your own courses.")
            return value

        raise serializers.ValidationError("You are not allowed to assign a course.")

    def create(self, validated_data):
        user = self.context['request'].user

        # If course is not provided or user is non-admin instructor,
        # optionally you might want to set it from context or prevent creation
        # Here, we assume course is provided and validated, so just call super()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Prevent non-admins/instructors from changing the course field
        if 'course' in validated_data:
            if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
                validated_data.pop('course', None)
            elif user.groups.filter(name="Instructor").exists() and validated_data['course'].created_by != user:
                # Instructors cannot reassign to other courses
                validated_data.pop('course', None)

        return super().update(instance, validated_data)
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
    
class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = '__all__'
        
        # fields = ['id', 'user', 'company_name', 'sponsorship_level']
    
class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsorship
        fields = ['id', 'sponsor', 'student', 'amount', 'status', 'utilization', 'created_at']
    
    def validate_sponsor(self, value):
        if value.user.role != 'sponsor':
            raise serializers.ValidationError("The selected user is not a sponsor.")
        return value

    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError("The selected user is not a student.")
        return value
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ['id', 'user', 'message', 'type', 'is_read', 'created_at']
    
class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmailLog
        fields = '__all__'

