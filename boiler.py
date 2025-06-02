import os
import sys
import subprocess
from pathlib import Path
import shutil
import re

# Import the user model customizer
try:
    from user_model_customizer import customize_user_model
except ImportError:
    print("Warning: user_model_customizer.py not found. User model customization will be skipped.")
    customize_user_model = None

def create_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e)
        sys.exit(1)

def update_import_statements(app_dir, old_app_name="authentification", new_app_name=None):
    """
    Update import statements in Python files to use the new app name
    
    Args:
        app_dir (str): Path to the app directory
        old_app_name (str): Old app name to replace (default: "authentification")
        new_app_name (str): New app name to use in imports
    """
    if not new_app_name:
        print("Error: new_app_name is required")
        return
    
    app_path = Path(app_dir)
    
    if not app_path.exists():
        print(f"Warning: App directory {app_dir} not found")
        return
    
    # Find all Python files in the app directory
    python_files = list(app_path.glob("**/*.py"))
    
    if not python_files:
        print(f"No Python files found in {app_dir}")
        return
    
    print(f"Updating import statements from '{old_app_name}' to '{new_app_name}'...")
    
    for py_file in python_files:
        try:
            # Read the file content
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern to match various import formats
            import_patterns = [
                # from .authentification import something
                (rf'from \.{re.escape(old_app_name)}', f'from .{new_app_name}'),
                # from authentification import something
                (rf'from {re.escape(old_app_name)}(?=\s)', f'from {new_app_name}'),
                # import authentification.something
                (rf'import {re.escape(old_app_name)}(?=\.)', f'import {new_app_name}'),
                # from authentification.something import
                (rf'from {re.escape(old_app_name)}\.', f'from {new_app_name}.'),
            ]
            
            # Apply all patterns
            for pattern, replacement in import_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Check if any changes were made
            if content != original_content:
                # Write the updated content back to the file
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Updated: {py_file.relative_to(app_path)}")
            
        except Exception as e:
            print(f"  Error updating {py_file}: {e}")
    
    print(f"Import statement update completed for {app_dir}")

def copy_authentication_files(source_dir, dest_dir, app_name):
    """
    Copy files from /authentification to the new app directory and update imports
    
    Args:
        source_dir (str): Source directory path
        dest_dir (str): Destination directory path  
        app_name (str): New app name for updating imports
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    if source_path.exists():
        try:
            # Copy all files from source to destination
            for item in source_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, dest_path)
                    print(f"Copied: {item.name}")
                elif item.is_dir():
                    dest_subdir = dest_path / item.name
                    shutil.copytree(item, dest_subdir, dirs_exist_ok=True)
                    print(f"Copied directory: {item.name}")
            
            # Update import statements in the copied files
            update_import_statements(dest_dir, "authentification", app_name)
            
        except Exception as e:
            print(f"Error copying files: {e}")
    else:
        print(f"Warning: Source directory {source_dir} not found. Skipping file copy.")

def check_existing_venv():
    """Check for existing virtual environments in current directory"""
    common_venv_names = ['venv', 'env', '.venv', 'virtualenv']
    existing_venvs = []
    
    for venv_name in common_venv_names:
        venv_path = Path(venv_name)
        if venv_path.exists() and venv_path.is_dir():
            # Check if it's a valid virtual environment
            if sys.platform == 'win32':
                python_exe = venv_path / 'Scripts' / 'python.exe'
                activate_script = venv_path / 'Scripts' / 'activate.bat'
            else:
                python_exe = venv_path / 'bin' / 'python'
                activate_script = venv_path / 'bin' / 'activate'
            
            if python_exe.exists() and activate_script.exists():
                existing_venvs.append(venv_name)
    
    return existing_venvs

def main():
    # Get project details
    project_name = input("Enter your Django project name: ").strip()
    app_name = input("Enter authentication app name: ").strip()
    
    # Check for existing virtual environments
    existing_venvs = check_existing_venv()
    
    if existing_venvs:
        print(f"\nFound existing virtual environment(s): {', '.join(existing_venvs)}")
        use_existing = input(f"Use existing virtual environment '{existing_venvs[0]}'? (y/n): ").lower().strip() == 'y'
        
        if use_existing:
            env_name = existing_venvs[0]
            print(f"Using existing virtual environment: {env_name}")
        else:
            if len(existing_venvs) > 1:
                print("Available virtual environments:")
                for i, venv in enumerate(existing_venvs, 1):
                    print(f"  {i}. {venv}")
                choice = input("Select virtual environment (enter number) or create new (press Enter): ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(existing_venvs):
                    env_name = existing_venvs[int(choice) - 1]
                    print(f"Using virtual environment: {env_name}")
                else:
                    env_name = input("Enter new virtual environment name (default: venv): ").strip() or 'venv'
            else:
                env_name = input("Enter new virtual environment name (default: venv): ").strip() or 'venv'
    else:
        env_name = input("Enter virtual environment name (default: venv): ").strip() or 'venv'

    # Determine activation command based on OS
    if sys.platform == 'win32':
        activate_cmd = f"{env_name}\\Scripts\\activate"
        pip_cmd = f"{env_name}\\Scripts\\pip"
        python_cmd = f"{env_name}\\Scripts\\python"
    else:
        activate_cmd = f"source {env_name}/bin/activate"
        pip_cmd = f"{env_name}/bin/pip"
        python_cmd = f"{env_name}/bin/python"

    # Create virtual environment if it doesn't exist
    venv_path = Path(env_name)
    if not venv_path.exists():
        print(f"\nCreating virtual environment: {env_name}")
        run_command(f"python -m venv {env_name}")
    else:
        print(f"\nUsing existing virtual environment: {env_name}")
    
    # Install packages from requirements.txt
    print("\nInstalling packages from requirements.txt...")
    if Path("requirements.txt").exists():
        run_command(f"{pip_cmd} install -r requirements.txt")
    else:
        print("Warning: requirements.txt not found. Please ensure it exists with the required packages.")
        return

    # Create Django project
    print(f"\nCreating Django project: {project_name}")
    run_command(f"{python_cmd} -m django startproject {project_name} .")

    # Create authentication app
    print(f"\nCreating authentication app: {app_name}")
    run_command(f"{python_cmd} manage.py startapp {app_name}")

    # Copy files from /authentification to the new app
    print(f"\nCopying authentication files to {app_name} app...")
    copy_authentication_files("authentification_folder", app_name, app_name)

    # User model customization
    if customize_user_model:
        print(f"\n{'='*60}")
        print("USER MODEL CUSTOMIZATION")
        print(f"{'='*60}")
        customize_models = input("Do you want to customize the User model? (y/n): ").lower().strip() == 'y'
        
        if customize_models:
            success = customize_user_model(app_name)
            if success:
                print("✅ User model customized successfully!")
            else:
                print("❌ User model customization failed, using default model.")
        else:
            print("ℹ️  Using default User model configuration.")
    else:
        print("⚠️  User model customization not available. Using default configuration.")

    # Create .env file
    env_content = """# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email Settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Database (if using PostgreSQL)
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
"""
    create_file(".env", env_content)
    print("Created .env file with default settings")

    # Update project settings
    settings_path = Path(project_name) / 'settings.py'
    
    # Read current settings
    with open(settings_path, 'r') as f:
        settings_content = f.read()
    
    # Add imports at the top
    imports_to_add = """from datetime import timedelta
from decouple import config
"""
    
    # Insert imports after existing imports
    if "from pathlib import Path" in settings_content:
        settings_content = settings_content.replace(
            "from pathlib import Path",
            f"from pathlib import Path\n{imports_to_add}"
        )
    else:
        settings_content = imports_to_add + "\n" + settings_content

    # Update SECRET_KEY to use environment variable
    secret_key_pattern = r"SECRET_KEY = ['\"][^'\"]*['\"]"
    settings_content = re.sub(
        secret_key_pattern,
        "SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')",
        settings_content
    )
    
    # Update DEBUG to use environment variable
    settings_content = settings_content.replace(
        "DEBUG = True",
        "DEBUG = config('DEBUG', default=True, cast=bool)"
    )

    # Add app to INSTALLED_APPS
    if "INSTALLED_APPS = [" in settings_content:
        settings_content = settings_content.replace(
            "INSTALLED_APPS = [",
            f"""INSTALLED_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    '{app_name}',"""
        )

    # Add CORS middleware
    if "MIDDLEWARE = [" in settings_content:
        settings_content = settings_content.replace(
            "MIDDLEWARE = [",
            """MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',"""
        )

    # Add REST Framework and JWT settings
    rest_framework_settings = f"""

# Custom User Model
AUTH_USER_MODEL = '{app_name}.User'

# Custom Commands Module
COMMANDS_MODULE = '{app_name}.management.commands'

# REST Framework Settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}}

# Simple JWT Settings
SIMPLE_JWT = {{
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}}

# Default User Preferences
DEFAULT_USER_PREFERENCES = {{
    "theme": "light",
    "notifications": {{"email": True, "push": True}},
}}

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
"""

    # Add settings to the end of the file
    settings_content += rest_framework_settings

    # Write updated settings
    create_file(settings_path, settings_content)
    print("Updated settings.py with authentication and email configuration")

    # Update project URLs to include app URLs
    project_urls_path = Path(project_name) / 'urls.py'
    project_urls_content = f"""from django.contrib import admin
from django.urls import path, include

path_v1 = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{{path_v1}}/', include('{app_name}.urls')),
]
"""
    create_file(project_urls_path, project_urls_content)
    print("Updated project URLs")

    # Run migrations
    print("\nMaking migrations...")
    run_command(f"{python_cmd} manage.py makemigrations")
    
    print("Running migrations...")
    run_command(f"{python_cmd} manage.py migrate")

    # Create superuser option
    create_superuser = input("\nCreate superuser? (y/n): ").lower().strip() == 'y'
    if create_superuser:
        run_command(f"{python_cmd} manage.py createsuperadmin")

    # Start development server
    start_server = input("\nStart development server now? (y/n): ").lower().strip() == 'y'
    if start_server:
        print(f"\nStarting development server...")
        print("Server will start at http://127.0.0.1:8000/")
        print("Press Ctrl+C to stop the server")
        run_command(f"{python_cmd} manage.py runserver")
    else:
        print("\n" + "="*60)
        print("Setup complete! Your Django project is ready.")
        print("="*60)
        print(f"\nTo start the development server:")
        print(f"1. Activate virtual environment:")
        if sys.platform == 'win32':
            print(f"   {env_name}\\Scripts\\activate")
        else:
            print(f"   source {env_name}/bin/activate")
        print("2. Run: python manage.py runserver")
        print("\nDon't forget to:")
        print("1. Update your .env file with actual email credentials")
        print("2. Update SECRET_KEY in .env file")
        print(f"3. Customize the {app_name} app as needed")
        print("\nAuthentication endpoints will be available at:")
        print("  - /api/v1/ (based on your app's URL configuration)")

if __name__ == "__main__":
    main()