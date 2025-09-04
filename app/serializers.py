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
        
# Assessment Serializer
class AssessmentSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(required=False)
    class Meta:
        model = models.Assessment
         # Include all relevant fields, including module and quiz
        fields = ['id', 'course','module' ,'title', 'due_date', 'max_score']

    def get_fields(self):
        """
        Dynamically adjust serializer fields based on the user role.
        For Students and Sponsors, make 'course' read-only.
        """
        fields = super().get_fields()
        user = self.context['request'].user
        # Make 'course' read-only for Students/Sponsors or Only Admins and Instructors can modify 'course
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
        if user.groups.filter(name="Admin").exists():
            return value
        if user.groups.filter(name="Instructor").exists():
            if value.created_by != user:
                raise serializers.ValidationError("You can only assign assessments to your own courses.")
            return value
        raise serializers.ValidationError("You are not allowed to assign a course.")
    
    def validate(self, attrs):
        if not attrs.get('module'):
            raise serializers.ValidationError("Assessment must be linked to a module.")
        return attrs
    
    def create(self, validated_data):
        module_data = validated_data.pop('module', None)

        # Create assessment first with quiz or empty module
        assessment = models.Assessment(**validated_data)

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
        read_only_fields = ['created_at']  # sponsor is selectable when student applies

    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError("The selected user is not a student.")
        return value

    def validate_sponsor(self, value):
        if value.user.role != 'sponsor':
            raise serializers.ValidationError("The selected user is not a sponsor.")
        return value

    def validate_amount(self, value):
        request = self.context['request']
        user = request.user

        if user.role == 'sponsor':  # when approving directly
            sponsor = models.Sponsor.objects.get(user=user)
            if sponsor.funds_provided < value:
                raise serializers.ValidationError("Insufficient funds in sponsor account.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        # Student applies → pending
        if user.role == 'student':
            validated_data['status'] = 'pending'
            validated_data['student'] = user
            sponsorship = super().create(validated_data)

            # Notify student
            models.Notification.objects.create(
                user=user,
                message=f"Your sponsorship application to {sponsorship.sponsor.company_name} is pending review."
            )

            # Notify specific sponsor
            models.Notification.objects.create(
                user=sponsorship.sponsor.user,
                message=f"New sponsorship request from {user.username} for amount {sponsorship.amount}."
            )

            return sponsorship

        # Sponsor directly funds → approve + deduct
        elif user.role == 'sponsor':
            sponsor = models.Sponsor.objects.get(user=user)
            amount = validated_data['amount']

            if sponsor.funds_provided < amount:
                raise serializers.ValidationError("Not enough funds to approve this sponsorship.")

            sponsor.funds_provided -= amount
            sponsor.save()

            validated_data['sponsor'] = sponsor
            validated_data['status'] = 'approved'
            sponsorship = super().create(validated_data)

            # Notify student
            models.Notification.objects.create(
                user=sponsorship.student,
                message=f"Your sponsorship request has been approved for {sponsorship.amount}."
            )
            return sponsorship

        raise serializers.ValidationError("Only students can apply or sponsors can approve sponsorships.")

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.role == 'sponsor' and instance.status == 'pending':
            action = validated_data.get("status")

            # Approve request
            if action == 'approved':
                sponsor = models.Sponsor.objects.get(user=user)
                amount = validated_data.get('amount', instance.amount)

                if sponsor.funds_provided < amount:
                    raise serializers.ValidationError("Not enough funds to approve this sponsorship.")

                sponsor.funds_provided -= amount
                sponsor.save()

                instance.sponsor = sponsor
                instance.amount = amount
                instance.status = 'approved'
                instance.save()

                # Notify student
                models.Notification.objects.create(
                    user=instance.student,
                    message=f"Your sponsorship request has been approved for {instance.amount}."
                )
                return instance

            # Reject request
            elif action == 'rejected':
                instance.status = 'rejected'
                instance.save()

                # Notify student
                models.Notification.objects.create(
                    user=instance.student,
                    message=f"Your sponsorship request to {instance.sponsor.company_name} has been rejected."
                )
                return instance

        return super().update(instance, validated_data)


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
        read_only_fields = ['user']
        # Optional: make user read-only if email logs track sender


class QuizAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all(),
        write_only=True
    )

    class Meta:
        model = models.Answer
        fields = ['question', 'text', 'is_correct']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.groups.filter(name='Student').exists():
            rep.pop('is_correct', None)
        return rep
        
class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, required=False)
    class Meta:
        model=models.Question
        fields=['text','answers']
    
    def validate_answers(self, value):
        """
        Ensure exactly 4 answers and only one correct answer.
        """
        if len(value) != 4:
            raise serializers.ValidationError("Each question must have exactly 4 answers.")
        
        correct_count = sum(1 for ans in value if ans.get('is_correct'))
        if correct_count != 1:
            raise serializers.ValidationError("There must be exactly one correct answer per question.")
        
        return value
        
class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, required=False)

    class Meta:
        model = models.Quiz
        fields = ['id', 'course', 'title', 'description', 'created_by', 'questions']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        user = self.context['request'].user
        validated_data['created_by'] = user

        quiz = super().create(validated_data)

        # 🔹 Create nested questions & answers
        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = models.Question.objects.create(quiz=quiz, **question_data)
            for answer_data in answers_data:
                models.Answer.objects.create(question=question, **answer_data)

        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])

        # Update main quiz fields
        instance = super().update(instance, validated_data)

        if questions_data:
            # 🔹 Remove existing questions & answers
            instance.question_set.all().delete()

            # 🔹 Recreate questions & answers
            for question_data in questions_data:
                answers_data = question_data.pop('answers', [])
                question = models.Question.objects.create(quiz=instance, **question_data)
                for answer_data in answers_data:
                    models.Answer.objects.create(question=question, **answer_data)

        return instance

    
    
class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAnswer
        fields = ['question', 'selected_answer']

    def validate(self, data):
        question = data['question']
        answer = data.get('selected_answer')

        # Ensure answer belongs to the question
        if answer and answer.question != question:
            raise serializers.ValidationError("Selected answer does not belong to the question.")
        return data


class StudentSubmissionSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True)
    percentage = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()

    class Meta:
        model = models.StudentSubmission
        fields = ['quiz', 'answers', 'score', 'percentage', 'passed']
        read_only_fields = ['score', 'percentage', 'passed']

    def validate_quiz(self, value):
        student = self.context['request'].user

        if not models.Enrollment.objects.filter(student=student, course=value.course).exists():
            raise serializers.ValidationError("You are not enrolled in this course.")

        if models.StudentSubmission.objects.filter(student=student, quiz=value).exists():
            raise serializers.ValidationError("You have already submitted this quiz.")

        return value

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student = self.context['request'].user

        # Create submission
        submission = models.StudentSubmission.objects.create(student=student, **validated_data)

        score = 0
        total_questions = submission.quiz.questions.count()  # fixed related_name

        for ans_data in answers_data:
            student_answer = models.StudentAnswer.objects.create(submission=submission, **ans_data)
            if student_answer.selected_answer and student_answer.selected_answer.is_correct:
                score += 1

        # Update submission
        submission.score = score
        submission.percentage = round((score / total_questions) * 100, 2) if total_questions > 0 else 0
        submission.passed = (score / total_questions) >= 0.5 if total_questions > 0 else False
        submission.save()

        return submission

    def get_percentage(self, obj):
        return obj.percentage

    def get_passed(self, obj):
        return obj.passed
