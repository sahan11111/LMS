from rest_framework import serializers
from . import models


# ──────────────────────── Course ────────────────────────
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'difficulty_level', 'created_by']
        read_only_fields = ['created_by']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user and request.user.groups.filter(name='Admin').exists():
            fields['created_by'].read_only = False
        return fields

    def validate_created_by(self, value):
        user = self.context['request'].user
        if user.groups.filter(name='Admin').exists():
            return value
        if user.groups.filter(name='Instructor').exists():
            if value != user:
                raise serializers.ValidationError(
                    'Instructors can only assign themselves as the course creator.'
                )
            return value
        raise serializers.ValidationError('You are not allowed to create courses.')

    def create(self, validated_data):
        user = self.context['request'].user
        if 'created_by' not in validated_data:
            validated_data['created_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'created_by' in validated_data and not user.groups.filter(name='Admin').exists():
            validated_data.pop('created_by', None)
        return super().update(instance, validated_data)


# ──────────────────────── Enrollment ────────────────────────
class EnrollmentSerializer(serializers.ModelSerializer):
    progress = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=False)

    class Meta:
        model = models.Enrollment
        fields = ['id', 'student', 'course', 'status', 'progress']
        read_only_fields = ['student']

    def validate(self, data):
        user = self.context['request'].user
        if user.role != 'student':
            raise serializers.ValidationError('Only students can enroll in courses.')

        # Check for duplicate enrollment on create
        if not self.instance:
            course = data.get('course')
            if course and models.Enrollment.objects.filter(student=user, course=course).exists():
                raise serializers.ValidationError('You are already enrolled in this course.')
        return data

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


# ──────────────────────── Lesson / Module ────────────────────────
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


# ──────────────────────── Assessment ────────────────────────
class AssessmentSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(required=False)

    class Meta:
        model = models.Assessment
        fields = ['id', 'course', 'module', 'title', 'due_date', 'max_score']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            if not (user.groups.filter(name='Admin').exists() or user.groups.filter(name='Instructor').exists()):
                fields['course'].read_only = True
        return fields

    def validate_course(self, value):
        user = self.context['request'].user
        if user.groups.filter(name='Admin').exists():
            return value
        if user.groups.filter(name='Instructor').exists():
            if value.created_by != user:
                raise serializers.ValidationError('You can only assign assessments to your own courses.')
            return value
        raise serializers.ValidationError('You are not allowed to assign a course.')

    def validate(self, attrs):
        if not attrs.get('module'):
            raise serializers.ValidationError('Assessment must be linked to a module.')
        return attrs

    def create(self, validated_data):
        module_data = validated_data.pop('module', None)
        assessment = models.Assessment(**validated_data)

        if module_data:
            lessons_data = module_data.pop('lessons', [])
            module = models.Module.objects.create(
                title=module_data['title'],
                description=module_data.get('description', ''),
                course=assessment.course,
                created_by=self.context['request'].user,
            )
            assessment.module = module

        assessment.save()

        if module_data and lessons_data:
            for lesson_data in lessons_data:
                lesson_contents_data = lesson_data.pop('lesson_contents', [])
                lesson = models.Lesson.objects.create(
                    module=assessment.module,
                    title=lesson_data['title'],
                    content=lesson_data.get('content', ''),
                )
                for content_data in lesson_contents_data:
                    models.LessonContent.objects.create(
                        lesson=lesson,
                        title=content_data['title'],
                        content_type=content_data['content_type'],
                        file=content_data.get('file'),
                    )

        return assessment

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'course' in validated_data:
            if not (user.groups.filter(name='Admin').exists() or user.groups.filter(name='Instructor').exists()):
                validated_data.pop('course', None)
            elif user.groups.filter(name='Instructor').exists() and validated_data['course'].created_by != user:
                validated_data.pop('course', None)
        return super().update(instance, validated_data)


# ──────────────────────── Submission ────────────────────────
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = ['id', 'assessment', 'student', 'content', 'score', 'submitted_at']
        read_only_fields = ['student', 'score', 'submitted_at']

    def validate_assessment(self, value):
        if not value:
            raise serializers.ValidationError('Assessment is required.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['student'] = request.user
        return super().create(validated_data)


class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = ['score']


# ──────────────────────── Sponsor ────────────────────────
class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = ['id', 'user', 'company_name', 'funds_provided']
        read_only_fields = ['user']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user and request.user.groups.filter(name='Admin').exists():
            fields['user'].read_only = False
        return fields

    def validate_user(self, value):
        if hasattr(value, 'role') and value.role != 'sponsor':
            raise serializers.ValidationError('The selected user is not a sponsor.')
        return value

    def create(self, validated_data):
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ──────────────────────── Sponsorship ────────────────────────
class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsorship
        fields = ['id', 'sponsor', 'student', 'amount', 'status', 'utilization', 'created_at']
        read_only_fields = ['created_at']

    def validate_student(self, value):
        if value.role != 'student':
            raise serializers.ValidationError('The selected user is not a student.')
        return value

    def validate_sponsor(self, value):
        if value.user.role != 'sponsor':
            raise serializers.ValidationError('The selected user is not a sponsor.')
        return value

    def validate_amount(self, value):
        user = self.context['request'].user
        if user.role == 'sponsor':
            try:
                sponsor = models.Sponsor.objects.get(user=user)
                if sponsor.funds_provided < value:
                    raise serializers.ValidationError('Insufficient funds in sponsor account.')
            except models.Sponsor.DoesNotExist:
                raise serializers.ValidationError('Sponsor profile not found.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        if user.role == 'student':
            validated_data['status'] = 'pending'
            validated_data['student'] = user
            sponsorship = super().create(validated_data)

            models.Notification.objects.create(
                user=user,
                message=f"Your sponsorship application to {sponsorship.sponsor.company_name or 'a sponsor'} is pending review.",
                type='sponsorship',
            )
            models.Notification.objects.create(
                user=sponsorship.sponsor.user,
                message=f"New sponsorship request from {user.username} for amount {sponsorship.amount}.",
                type='sponsorship',
            )
            return sponsorship

        elif user.role == 'sponsor':
            sponsor = models.Sponsor.objects.get(user=user)
            amount = validated_data['amount']

            if sponsor.funds_provided < amount:
                raise serializers.ValidationError('Not enough funds to approve this sponsorship.')

            sponsor.funds_provided -= amount
            sponsor.save()

            validated_data['sponsor'] = sponsor
            validated_data['status'] = 'approved'
            sponsorship = super().create(validated_data)

            models.Notification.objects.create(
                user=sponsorship.student,
                message=f"Your sponsorship request has been approved for {sponsorship.amount}.",
                type='sponsorship',
            )
            return sponsorship

        raise serializers.ValidationError('Only students can apply or sponsors can approve sponsorships.')

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.role == 'sponsor' and instance.status == 'pending':
            new_status = validated_data.get('status')

            if new_status == 'approved':
                sponsor = models.Sponsor.objects.get(user=user)
                amount = validated_data.get('amount', instance.amount)

                if sponsor.funds_provided < amount:
                    raise serializers.ValidationError('Not enough funds to approve this sponsorship.')

                sponsor.funds_provided -= amount
                sponsor.save()

                instance.sponsor = sponsor
                instance.amount = amount
                instance.status = 'approved'
                instance.save()

                models.Notification.objects.create(
                    user=instance.student,
                    message=f"Your sponsorship request has been approved for {instance.amount}.",
                    type='sponsorship',
                )
                return instance

            elif new_status == 'rejected':
                instance.status = 'rejected'
                instance.save()

                models.Notification.objects.create(
                    user=instance.student,
                    message=f"Your sponsorship request to {instance.sponsor.company_name or 'a sponsor'} has been rejected.",
                    type='sponsorship',
                )
                return instance

        return super().update(instance, validated_data)


# ──────────────────────── Notification ────────────────────────
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ['id', 'user', 'message', 'type', 'is_read', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ──────────────────────── Email Log ────────────────────────
class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmailLog
        fields = '__all__'
        read_only_fields = ['user']


# ──────────────────────── Quiz ────────────────────────
class QuizAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all(),
        write_only=True,
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
        model = models.Question
        fields = ['text', 'answers']

    def validate_answers(self, value):
        if len(value) != 4:
            raise serializers.ValidationError('Each question must have exactly 4 answers.')

        correct_count = sum(1 for ans in value if ans.get('is_correct'))
        if correct_count != 1:
            raise serializers.ValidationError('There must be exactly one correct answer per question.')

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

        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = models.Question.objects.create(quiz=quiz, **question_data)
            for answer_data in answers_data:
                answer_data.pop('question', None)
                models.Answer.objects.create(question=question, **answer_data)

        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])
        instance = super().update(instance, validated_data)

        if questions_data:
            instance.questions.all().delete()
            for question_data in questions_data:
                answers_data = question_data.pop('answers', [])
                question = models.Question.objects.create(quiz=instance, **question_data)
                for answer_data in answers_data:
                    answer_data.pop('question', None)
                    models.Answer.objects.create(question=question, **answer_data)

        return instance


# ──────────────────────── Student Quiz Submission ────────────────────────
class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAnswer
        fields = ['question', 'selected_answer']

    def validate(self, data):
        question = data['question']
        answer = data.get('selected_answer')
        if answer and answer.question != question:
            raise serializers.ValidationError('Selected answer does not belong to the question.')
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
            raise serializers.ValidationError('You are not enrolled in this course.')

        if models.StudentSubmission.objects.filter(student=student, quiz=value).exists():
            raise serializers.ValidationError('You have already submitted this quiz.')

        return value

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student = self.context['request'].user

        submission = models.StudentSubmission.objects.create(student=student, **validated_data)

        score = 0
        total_questions = submission.quiz.questions.count()

        for ans_data in answers_data:
            student_answer = models.StudentAnswer.objects.create(submission=submission, **ans_data)
            if student_answer.selected_answer and student_answer.selected_answer.is_correct:
                score += 1

        submission.score = score
        submission.percentage = round((score / total_questions) * 100, 2) if total_questions > 0 else 0
        submission.passed = (score / total_questions) >= 0.5 if total_questions > 0 else False
        submission.save()

        return submission

    def get_percentage(self, obj):
        return obj.percentage

    def get_passed(self, obj):
        return obj.passed