from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    Batch, StudentProfile, Course, Module
)


class BatchModelTest(TestCase):
    def setUp(self):
        self.batch = Batch.objects.create(
            name="Test Batch 2026",
            start_date="2026-01-01",
            end_date="2026-12-31",
            is_active=True
        )
    
    def test_batch_creation(self):
        self.assertEqual(self.batch.name, "Test Batch 2026")
        self.assertTrue(self.batch.is_active)


class StudentProfileTest(TestCase):
    def setUp(self):
        self.batch = Batch.objects.create(
            name="Test Batch",
            start_date="2026-01-01",
            end_date="2026-12-31"
        )
        self.user = User.objects.create_user(
            username="teststudent",
            password="testpass123",
            first_name="Test",
            last_name="Student"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            student_id="STU001",
            phone="1234567890",
            batch=self.batch
        )
    
    def test_student_profile_creation(self):
        self.assertEqual(self.profile.student_id, "STU001")
        self.assertEqual(self.profile.user.username, "teststudent")


class CourseTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            is_active=True
        )
    
    def test_course_creation(self):
        self.assertEqual(self.course.title, "Test Course")
        self.assertTrue(self.course.is_active)





class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.batch = Batch.objects.create(
            name="Test Batch",
            start_date="2026-01-01",
            end_date="2026-12-31"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            student_id="STU001",
            phone="1234567890",
            batch=self.batch
        )
    
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_required_for_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_access_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
