# Codex Project

A Django web application that allows users to register and login with different roles (USER, TEACHER, ADMIN) and access role-specific dashboards. The platform includes a comprehensive content management system for educational materials.

## Features

- User registration and authentication
- Role-based permissions and dashboards
- Custom user model
- Bootstrap-styled responsive interface
- Admin interface for user management
- Content management system for educational materials
- Course creation and management
- Module-based learning structure
- Student enrollment and progress tracking
- Multiple content types (text, files, images, videos, assignments)

## Setup

1. Clone the repository:
```
git clone <repository-url>
cd codex-python
```

2. Create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install django pillow
```

4. Run migrations:
```
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```

6. Run the development server:
```
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/user/login/

## Default Accounts

A default admin account has been created:
- Username: admin
- Password: adminpassword

## Project Structure

- `codex_project/` - Main project settings
- `user_management/` - App for user registration, authentication, and dashboards
  - `models.py` - Custom User model with roles
  - `views.py` - Views for registration, login, and dashboards
  - `templates/` - HTML templates for the application
  - `forms.py` - Forms for user creation and authentication
  - `urls.py` - URL routing
- `content_management/` - App for educational content management
  - `models.py` - Models for courses, modules, and various content types
  - `views.py` - Views for content creation, editing, and student interaction
  - `templates/` - HTML templates for content management
  - `urls.py` - URL routing for content features
  - `admin.py` - Admin interface configuration

## Usage

1. Register a new account or log in with the default admin account
2. Access your role-specific dashboard:
   - **Students** can browse and enroll in courses, track their progress, and access learning materials
   - **Teachers** can create and manage courses, organize content into modules, and add various types of learning materials
   - **Admins** can manage users and have full access to all courses and content

3. Content Management:
   - Create courses with descriptions and categorize them by subject
   - Organize course content into modules
   - Add different types of content: text, files, images, videos, and assignments
   - Track student progress through course modules

4. User Management:
   - Admin users can create, edit, and delete users
   - Assign different roles to users (User/Student, Teacher, Admin)
   - View system statistics and user activity