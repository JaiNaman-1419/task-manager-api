# Task Manager API

A comprehensive RESTful API for managing tasks with user authentication, built with Django REST Framework.

## Features

- **Complete CRUD Operations** for tasks
- **JWT Authentication** with refresh tokens
- **User Registration and Login**
- **Role-based Access Control** (Admin/Regular User)
- **Task Filtering and Search**
- **Pagination Support**
- **API Documentation** with Swagger/ReDoc
- **Comprehensive Test Suite**
- **Admin Interface**

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Testing**: Django's built-in testing framework

## Quick Start

### Prerequisites

- Python 3.13+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd task_manager
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the project root:
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

7. **Start the development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Django Admin**: http://localhost:8000/admin/

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register/` | User registration | None |
| POST | `/api/auth/login/` | User login | None |
| POST | `/api/auth/token/refresh/` | Refresh access token | None |
| GET | `/api/auth/profile/` | Get user profile | Required |

### Task Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/tasks/` | List all tasks | Required |
| POST | `/api/tasks/` | Create new task | Required |
| GET | `/api/tasks/{id}/` | Get specific task | Required |
| PUT | `/api/tasks/{id}/` | Update specific task | Required |
| PATCH | `/api/tasks/{id}/` | Partially update task | Required |
| DELETE | `/api/tasks/{id}/` | Delete specific task | Required |
| GET | `/api/tasks/stats/` | Get task statistics | Required |

## Request/Response Examples

### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-access-token>" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user": "john@example.com"
}
```

### List Tasks with Filtering
```bash
# Get all tasks
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks/

# Get completed tasks only
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks/?completed=true

# Search tasks by title
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks/?search=documentation

# Pagination
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks/?page=2
```

### Update Task
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-access-token>" \
  -d '{
    "completed": true
  }'
```

### Get Task Statistics
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks/stats/
```

**Response:**
```json
{
  "total_tasks": 10,
  "completed_tasks": 7,
  "pending_tasks": 3,
  "completion_rate": 70.0
}
```

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. After login/registration, you'll receive:

- **Access Token**: Short-lived token for API requests (60 minutes)
- **Refresh Token**: Long-lived token to get new access tokens (7 days)

### Using Authentication

Include the access token in the Authorization header:
```
Authorization: Bearer <your-access-token>
```

### Token Refresh

When your access token expires, use the refresh token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your-refresh-token>"
  }'
```

## User Roles

### Regular User
- Can create, read, update, and delete their own tasks
- Can view their own task statistics
- Cannot access other users' tasks

### Admin User
- Can perform all operations on any task
- Can view all tasks and statistics
- Has access to Django admin interface

To create an admin user:
```bash
python manage.py createsuperuser
# Then update the user's role to 'admin' in Django admin or directly in database
```

## Filtering and Search

### Available Filters

- **completed**: Filter by completion status (`true`/`false`)
- **title**: Filter by title (case-insensitive contains)
- **created_at**: Filter by creation date range

### Search
- Search across title and description fields
- Use `?search=<term>` parameter

### Ordering
- Default: `-created_at` (newest first)
- Available fields: `created_at`, `updated_at`, `title`
- Use `?ordering=<field>` or `?ordering=-<field>` for descending

### Examples
```bash
# Completed tasks created in the last week
/api/tasks/?completed=true&created_at_after=2024-01-08

# Search and order
/api/tasks/?search=urgent&ordering=-updated_at

# Complex filtering
/api/tasks/?completed=false&title__icontains=project&ordering=created_at
```

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test tasks
python manage.py test accounts

# Run specific test class
python manage.py test tasks.tests.TaskAPITest

# Run specific test method
python manage.py test tasks.tests.TaskAPITest.test_create_task
```

### Test Coverage

Install coverage and run:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report -m
coverage html  # Generates htmlcov/ directory with detailed report
```

### Test Categories

- **Model Tests**: Test model creation, validation, and methods
- **API Tests**: Test all CRUD operations and permissions
- **Authentication Tests**: Test registration, login, and JWT functionality
- **Permission Tests**: Test role-based access control
- **Pagination Tests**: Test list pagination functionality

## Project Structure

```
task_manager/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .env                     # Environment variables (create this)
├── task_manager/            # Main project directory
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── accounts/                # User authentication app
│   ├── models.py            # Custom User model
│   ├── serializers.py       # User serializers
│   ├── views.py             # Authentication views
│   ├── urls.py              # Auth URL patterns
│   └── tests.py             # Authentication tests
└── tasks/                   # Task management app
    ├── models.py            # Task model
    ├── serializers.py       # Task serializers
    ├── views.py             # Task CRUD views
    ├── urls.py              # Task URL patterns
    ├── filters.py           # Task filtering logic
    ├── permissions.py       # Custom permissions
    ├── tests.py             # Task tests
    └── admin.py             # Admin interface
```

## Database Schema

### User Model
```python
User {
    id: AutoField (PK)
    username: CharField (unique)
    email: EmailField (unique)
    password: CharField (hashed)
    role: CharField (choices: 'admin', 'user')
    created_at: DateTimeField
    updated_at: DateTimeField
}
```

### Task Model
```python
Task {
    id: AutoField (PK)
    title: CharField (max_length=200)
    description: TextField (optional)
    completed: BooleanField (default=False)
    created_at: DateTimeField (auto_now_add=True)
    updated_at: DateTimeField (auto_now=True)
    user: ForeignKey (User, CASCADE)
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
SECRET_KEY=your-super-secret-django-key

# Optional (defaults shown)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (if using PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# JWT Settings (optional)
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days
```

### Database Configuration

#### SQLite (Default)
No additional configuration needed. Database file will be created automatically.

#### PostgreSQL
1. Install psycopg2: `pip install psycopg2-binary`
2. Update settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'task_manager',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### MySQL
1. Install mysqlclient: `pip install mysqlclient`
2. Update settings.py accordingly

## Deployment

### Production Checklist

1. **Security Settings**
   - Set `DEBUG=False`
   - Configure `ALLOWED_HOSTS`
   - Use strong `SECRET_KEY`
   - Enable HTTPS

2. **Database**
   - Use PostgreSQL/MySQL in production
   - Configure database backups

3. **Static Files**
   - Configure `STATIC_ROOT`
   - Use WhiteNoise or CDN

4. **Environment Variables**
   - Store sensitive data in environment variables
   - Use python-decouple for configuration

### Example Production Settings

```python
# production_settings.py
from .settings import *
import os

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## Changelog

### v1.0.0 (Current)
- Initial release
- Complete CRUD operations for tasks
- JWT authentication
- User registration and login
- Role-based access control
- Task filtering and search
- Pagination support
- Comprehensive test suite
- API documentation

## Roadmap

Future enhancements:
- [ ] Task categories/tags
- [ ] Task due dates and reminders
- [ ] File attachments
- [ ] Task sharing between users
- [ ] Email notifications
- [ ] Task templates
- [ ] Bulk operations
- [ ] Advanced reporting
- [ ] Mobile app integration
- [ ] Webhook support
