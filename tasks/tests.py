import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    """Test cases for Task model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_task_creation(self):
        """Test task creation"""
        task = Task.objects.create(
            title="Test Task", description="Test Description", user=self.user
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        self.assertTrue(task.created_at)
        self.assertTrue(task.updated_at)

    def test_task_str_representation(self):
        """Test task string representation"""
        task = Task.objects.create(title="Test Task", user=self.user)
        self.assertEqual(str(task), "Test Task")


class TaskAPITest(APITestCase):
    """Test cases for Task API endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", role="admin"
        )

        # Create test tasks
        self.task1 = Task.objects.create(
            title="User1 Task 1", description="Task 1 for user 1", user=self.user1
        )
        self.task2 = Task.objects.create(
            title="User1 Task 2", description="Task 2 for user 1", completed=True, user=self.user1
        )
        self.task3 = Task.objects.create(
            title="User2 Task 1", description="Task 1 for user 2", user=self.user2
        )

    def get_token(self, user):
        """Helper method to get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        """Helper method to authenticate user"""
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_tasks_unauthenticated(self):
        """Test getting tasks without authentication"""
        url = reverse("task-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_tasks_authenticated_user(self):
        """Test getting tasks as authenticated regular user"""
        self.authenticate(self.user1)
        url = reverse("task-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # User1 has 2 tasks

        # Check that user only sees their own tasks
        task_ids = [task["id"] for task in response.data["results"]]
        self.assertIn(self.task1.id, task_ids)
        self.assertIn(self.task2.id, task_ids)
        self.assertNotIn(self.task3.id, task_ids)

    def test_get_tasks_admin_user(self):
        """Test getting tasks as admin user"""
        self.authenticate(self.admin_user)
        url = reverse("task-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)  # Admin sees all tasks

    def test_create_task(self):
        """Test creating a new task"""
        self.authenticate(self.user1)
        url = reverse("task-list-create")
        data = {
            "title": "New Test Task",
            "description": "New test description",
            "completed": False,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Test Task")
        self.assertEqual(response.data["description"], "New test description")
        self.assertFalse(response.data["completed"])

    def test_create_task_invalid_data(self):
        """Test creating task with invalid data"""
        self.authenticate(self.user1)
        url = reverse("task-list-create")
        data = {"description": "Task without title"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_specific_task(self):
        """Test getting a specific task"""
        self.authenticate(self.user1)
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.task1.id)
        self.assertEqual(response.data["title"], self.task1.title)

    def test_get_task_not_owner(self):
        """Test getting task that doesn't belong to user"""
        self.authenticate(self.user1)
        url = reverse("task-detail", kwargs={"pk": self.task3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        """Test updating a task"""
        self.authenticate(self.user1)
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "completed": True,
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task Title")
        self.assertEqual(self.task1.description, "Updated description")
        self.assertTrue(self.task1.completed)

    def test_partial_update_task(self):
        """Test partially updating a task"""
        self.authenticate(self.user1)
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        data = {"completed": True}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.completed)
        self.assertEqual(self.task1.title, "User1 Task 1")  # Title unchanged

    def test_delete_task(self):
        """Test deleting a task"""
        self.authenticate(self.user1)
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task1.pk).exists())

    def test_admin_can_access_all_tasks(self):
        """Test that admin can access and modify any task"""
        self.authenticate(self.admin_user)

        # Admin can view any task
        url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin can update any task
        data = {"completed": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_filtering_by_completion(self):
        """Test filtering tasks by completion status"""
        self.authenticate(self.user1)
        url = reverse("task-list-create")

        # Filter completed tasks
        response = self.client.get(url, {"completed": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertTrue(response.data["results"][0]["completed"])

        # Filter incomplete tasks
        response = self.client.get(url, {"completed": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertFalse(response.data["results"][0]["completed"])

    def test_task_search(self):
        """Test searching tasks by title"""
        self.authenticate(self.user1)
        url = reverse("task-list-create")

        response = self.client.get(url, {"search": "Task 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["title"], "User1 Task 2")

    def test_task_stats(self):
        """Test task statistics endpoint"""
        self.authenticate(self.user1)
        url = reverse("task-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_tasks"], 2)
        self.assertEqual(response.data["completed_tasks"], 1)
        self.assertEqual(response.data["pending_tasks"], 1)
        self.assertEqual(response.data["completion_rate"], 50.0)


class AuthenticationTest(APITestCase):
    """Test cases for authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

    def test_user_registration(self):
        """Test user registration"""
        url = reverse("register")
        response = self.client.post(url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "test@example.com")

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        url = reverse("register")
        data = self.user_data.copy()
        data["password_confirm"] = "differentpass"
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username="existing", email="test@example.com", password="testpass123"
        )

        url = reverse("register")
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login"""
        # Create user first
        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        url = reverse("login")
        login_data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse("login")
        login_data = {"email": "nonexistent@example.com", "password": "wrongpass"}
        response = self.client.post(url, login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_user_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse("login")
        login_data = {"email": "test@example.com"}
        response = self.client.post(url, login_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profile(self):
        """Test getting user profile"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Authenticate user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["username"], "testuser")

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserModelTest(TestCase):
    """Test cases for User model"""

    def test_user_creation(self):
        """Test user creation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "user")  # Default role
        self.assertTrue(user.created_at)
        self.assertTrue(user.updated_at)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(str(user), "test@example.com")

    def test_admin_user_creation(self):
        """Test admin user creation"""
        admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", role="admin"
        )
        self.assertEqual(admin_user.role, "admin")


class PaginationTest(APITestCase):
    """Test cases for pagination"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create 25 tasks for pagination testing
        for i in range(25):
            Task.objects.create(
                title=f"Task {i+1}", description=f"Description for task {i+1}", user=self.user
            )

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_task_pagination(self):
        """Test task list pagination"""
        url = reverse("task-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        # Should have 25 total tasks
        self.assertEqual(response.data["count"], 25)
        # Should have 20 tasks per page (default PAGE_SIZE)
        self.assertEqual(len(response.data["results"]), 20)
        # Should have next page
        self.assertIsNotNone(response.data["next"])
        # Should not have previous page (first page)
        self.assertIsNone(response.data["previous"])

    def test_task_pagination_second_page(self):
        """Test second page of task pagination"""
        url = reverse("task-list-create")
        response = self.client.get(url, {"page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 5 tasks on second page (25 - 20)
        self.assertEqual(len(response.data["results"]), 5)
        # Should not have next page
        self.assertIsNone(response.data["next"])
        # Should have previous page
        self.assertIsNotNone(response.data["previous"])


class PermissionsTest(APITestCase):
    """Test cases for permissions"""

    def setUp(self):
        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", role="admin"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpass123"
        )

        self.task = Task.objects.create(
            title="Test Task", description="Test Description", user=self.regular_user
        )

        self.client = APIClient()

    def authenticate_user(self, user):
        """Helper to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_regular_user_can_crud_own_tasks(self):
        """Test that regular users can perform CRUD operations on their own tasks"""
        self.authenticate_user(self.regular_user)

        # Read own task
        url = reverse("task-detail", kwargs={"pk": self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update own task
        data = {"title": "Updated Title", "description": "Updated Description"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete own task
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_access_others_tasks(self):
        """Test that regular users cannot access other users' tasks"""
        self.authenticate_user(self.other_user)

        url = reverse("task-detail", kwargs={"pk": self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_access_all_tasks(self):
        """Test that admin users can access all tasks"""
        self.authenticate_user(self.admin_user)

        # Admin can read any task
        url = reverse("task-detail", kwargs={"pk": self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin can update any task
        data = {"title": "Admin Updated Title"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
