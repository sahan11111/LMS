from rest_framework import serializers
from . import models
from core.serializers import UserSerializer

# Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
    
    # Make created_by read-only for non-admins
    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.groups.filter(name="Admin").exists():  #Non-admins cannot edit created_by
            fields['created_by'].read_only = True
        return fields

    def validate_created_by(self, value):
        user = self.context['request'].user

        if user.groups.filter(name="Admin").exists(): 
            return value
        elif user.groups.filter(name="Instructor").exists():
            if value != user:
                raise serializers.ValidationError("Instructors can only assign themselves as the course creator.")
            return value
        raise serializers.ValidationError("You are not allowed to create courses.")

    def create(self, validated_data):
        user = self.context['request'].user
        if 'created_by' not in validated_data:
            validated_data['created_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'created_by' in validated_data and not user.groups.filter(name="Admin").exists():
            validated_data.pop('created_by', None)
        return super().update(instance, validated_data)

# Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        fields = ['id', 'student', 'course', 'status', 'progress']
        read_only_fields = ['student']  # auto-assign

    def validate(self, data):
        user = self.context['request'].user
        if user.role != 'student':
            raise serializers.ValidationError("Only students can enroll in courses.")
        return data

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user  # auto-assign
        return super().create(validated_data)

# Assessment Serializer
class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assessment
        fields = ['id', 'course', 'title', 'due_date', 'max_score']

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        # Make 'course' read-only for Students/Sponsors
        if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
            fields['course'].read_only = True
        return fields

    def validate_course(self, value):
        user = self.context['request'].user
        if user.groups.filter(name="Admin").exists():
            return value
        if user.groups.filter(name="Instructor").exists():
            if value.created_by != user:
                raise serializers.ValidationError("You can only assign assessments to your own courses.")
            return value
        raise serializers.ValidationError("You are not allowed to assign a course.")

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'course' in validated_data:
            if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
                validated_data.pop('course', None)
            elif user.groups.filter(name="Instructor").exists() and validated_data['course'].created_by != user:
                validated_data.pop('course', None)
        return super().update(instance, validated_data)

# Submission Serializer
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = ['id', 'assessment', 'student', 'score', 'submitted_at']
        read_only_fields = ['student']  # auto-assign

    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError("Only users with the student role can submit assessments.")
        return value

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user  # auto-assign
        return super().create(validated_data)

# Sponsor Serializer
class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = '__all__'

# Sponsorship Serializer
class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsorship
        fields = ['id', 'sponsor', 'student', 'amount', 'status', 'utilization', 'created_at']
        read_only_fields = ['sponsor']  # auto-assign

    def validate_sponsor(self, value):
        if value.user.role != 'sponsor':
            raise serializers.ValidationError("The selected user is not a sponsor.")
        return value

    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError("The selected user is not a student.")
        return value

    def create(self, validated_data):
        validated_data['sponsor'] = self.context['request'].user  # auto-assign
        return super().create(validated_data)

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ['id', 'user', 'message', 'type', 'is_read', 'created_at']
        read_only_fields = ['user']  # auto-assign

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # auto-assign
        return super().create(validated_data)

# Email Log Serializer
class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmailLog
        fields = '__all__'
        # Optional: make user read-only if email logs track sender
