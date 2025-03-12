# Codex Project

A Django web application that allows users to register and login with different roles (USER, TEACHER, ADMIN) and access role-specific dashboards.

## Features

- User registration and authentication
- Role-based permissions and dashboards
- Custom user model
- Bootstrap-styled responsive interface
- Admin interface for user management

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
pip install django
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

7. Access the application at http://127.0.0.1:8000/

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

## Usage

1. Register a new account or log in with the default admin account
2. Access your role-specific dashboard
3. Admin users can manage all users through the admin interface or admin dashboard