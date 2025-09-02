from rest_framework import serializers
from . import models

# Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
        read_only_fields = ['created_by']
    # Make created_by read-only for non-admins
    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.groups.filter(name="Admin").exists():  #Non-admins cannot edit created_by
            fields['created_by'].read_only = True
        return fields

    def validate_created_by(self, value):
        user = self.context['request'].user
        
        # Admin can assign freely
        if user.groups.filter(name="Admin").exists(): 
            return value
        # Instructor can only assign themselves
        elif user.groups.filter(name="Instructor").exists():
            if value != user:
                raise serializers.ValidationError("Instructors can only assign themselves as the course creator.")
            return value
        raise serializers.ValidationError("You are not allowed to create courses.") # Students/Sponsors cannot create courses

    def create(self, validated_data):
        user = self.context['request'].user
        if 'created_by' not in validated_data:
            validated_data['created_by'] = user # Instructor auto-assign
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'created_by' in validated_data and not user.groups.filter(name="Admin").exists(): #  Prevent non-admin changing creator
            validated_data.pop('created_by', None)
        return super().update(instance, validated_data)

# Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    progress = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=False)  
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

        
        
class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LessonContent
        fields = ['title', 'content_type', 'file']

class LessonSerializer(serializers.ModelSerializer):
    lesson_contents = LessonContentSerializer(many=True, required=False)

    class Meta:
        model = models.Lesson
        fields = ['title', 'content', 'lesson_contents']

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, required=False)

    class Meta:
        model = models.Module
        fields = ['title', 'description', 'lessons']
        # 'course' and 'created_by' will be set automatically when creating via Assessment
        # read_only_fields = ['id']
        
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = models.Question
        fields = ['id', 'text', 'answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = models.Quiz
        fields = ['id', 'title', 'description', 'questions']
        
# Assessment Serializer
class AssessmentSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(required=False)
    quiz=QuizSerializer(required=False) # nested quiz data
    
    
    class Meta:
        model = models.Assessment
         # Include all relevant fields, including module and quiz
        fields = ['id', 'course','module','quiz' ,'title', 'due_date', 'max_score']

    def get_fields(self):
        """
        Dynamically adjust serializer fields based on the user role.
        For Students and Sponsors, make 'course' read-only.
        """
        fields = super().get_fields()
        user = self.context['request'].user
        # Make 'course' read-only for Students/Sponsors or Only Admins and Instructors can modify 'course
        if not user or getattr(self, 'swagger_fake_view', False):
            fields['course'].read_only = False
        else:
            if not (user.groups.filter(name="Admin").exists() or user.groups.filter(name="Instructor").exists()):
                fields['course'].read_only = True
        return fields

    def validate_course(self, value):
        """
        Ensure only authorized users can assign a course to an assessment.
        - Admin: can assign any course
        - Instructor: can only assign courses they created
        - Others: cannot assign courses
        """
        
        user = self.context['request'].user
         
        #  Check if course is provided
        if not value:
            raise serializers.ValidationError("Course is required.")

        #  Permission checks
        if user.groups.filter(name="Admin").exists():
            return value
        elif user.groups.filter(name="Instructor").exists():
            if value.created_by != user:
                raise serializers.ValidationError("You can only assign assessments to your own courses.")
            return value
        else:
            raise serializers.ValidationError("You are not allowed to assign a course.")

    
    def validate(self, attrs):
        """
        Validate that the assessment is linked to either a module or a quiz,
        but not both. This mirrors the model's clean() method.
        """
        module = attrs.get('module')
        quiz = attrs.get('quiz')

        if not module and not quiz:
            raise serializers.ValidationError("Assessment must be linked to either a module or a quiz.")
        if module and quiz:
            raise serializers.ValidationError("Assessment cannot be linked to both module and quiz.")

        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        module_data = validated_data.pop('module', None)
        quiz_data = validated_data.pop('quiz', None)

        # Create the assessment instance first
        if 'course' not in validated_data or validated_data['course'] is None:
            if user.groups.filter(name="Instructor").exists():
                # Assign first course created by instructor automatically
                course = models.Course.objects.filter(created_by=user).first()
                if not course:
                    raise serializers.ValidationError("Instructor has no course to assign.")
                validated_data['course'] = course
            else:
                raise serializers.ValidationError("Course is required.")
            
        assessment = models.Assessment.objects.create(**validated_data)

        # If module data is provided, create Module and assign to assessment
        if module_data:
            lessons_data = module_data.pop('lessons', [])
            module = models.Module.objects.create(
                title=module_data['title'],
                description=module_data.get('description', ''),
                course=assessment.course,
                created_by=self.context['request'].user
            )
            assessment.module = module  # assign module BEFORE saving

        # Save assessment (will run full_clean correctly)
        assessment.save()

        # Now create Lessons and LessonContents
        if module_data and lessons_data:
            for lesson_data in lessons_data:
                lesson_contents_data = lesson_data.pop('lesson_contents', [])
                lesson = models.Lesson.objects.create(
                    module=assessment.module,
                    title=lesson_data['title'],
                    content=lesson_data.get('content', '')
                )
                for content_data in lesson_contents_data:
                    models.LessonContent.objects.create(
                        lesson=lesson,
                        title=content_data['title'],
                        content_type=content_data['content_type'],
                        file=content_data.get('file')
                    )
                    
        # If quiz data is provided, create Quiz and assign to assessment
        if quiz_data:
            questions_data = quiz_data.pop('questions', [])
            quiz=models.Quiz.objects.create(
                title=quiz_data['title'],
                description=quiz_data.get('description',''),
                course=assessment.course,
                created_by=self.context['request'].user
            )
            assessment.quiz=quiz
            assessment.save()  # Save again to update quiz field
            
            #create questions and answers
            for question_data in questions_data:
                answers_data = question_data.pop('answers', [])
                question = models.Question.objects.create(
                    quiz=quiz,
                    text=question_data['text']
                )
                for answer_data in answers_data:
                    models.Answer.objects.create(
                        question=question,
                        text=answer_data['text'],
                        is_correct=answer_data.get('is_correct', False)
                    )

        return assessment

    

    def update(self, instance, validated_data):
        """
        Restrict updates to 'course' field based on user role:
        - Students/Sponsors cannot update the course
        - Instructors can update only if they created the course
        """
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
        fields = ['id', 'assessment', 'student', 'content', 'score', 'submitted_at']
        read_only_fields = ['student', 'score', 'submitted_at']   # student auto-assigned, score only instructor updates

    def validate_assessment(self, value):
        """Ensure assessment exists and is valid."""
        if not value:
            raise serializers.ValidationError("Assessment is required.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["student"] = request.user
        return super().create(validated_data)
class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = ['score']


# Sponsor Serializer
class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = ['id', 'user', 'company_name', 'funds_provided']

    def validate_user(self, value):
        # Validate that the user assigned to this sponsor is actually a sponsor
        if hasattr(value, 'role') and value.role != 'sponsor':
            raise serializers.ValidationError("The selected user is not a sponsor.")
        return value
    
    def create(self, validated_data):
        validated_data['sponsor'] = self.context['request'].user  
        return super().create(validated_data)

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


