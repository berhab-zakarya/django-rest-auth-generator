import os
from pathlib import Path

def get_user_preferences():
    """
    Collect user preferences for model customization
    """
    preferences = {}
    
    print("\n" + "="*60)
    print("USER MODEL CUSTOMIZATION")
    print("="*60)
    
    # Ask about roles
    print("\n1. ROLE SYSTEM CONFIGURATION")
    print("-" * 30)
    customize_roles = input("Do you want to customize user roles? (y/n): ").lower().strip() == 'y'
    
    if customize_roles:
        print("\nDefault roles are: Admin, User")
        add_roles = input("Do you want to add additional roles? (y/n): ").lower().strip() == 'y'
        
        if add_roles:
            roles = []
            print("\nEnter role names (type '0' to finish):")
            while True:
                role = input("Role name: ").strip()
                if role == '0':
                    break
                if role:
                    roles.append(role)
            preferences['custom_roles'] = roles
        else:
            preferences['custom_roles'] = []
    else:
        preferences['use_roles'] = False
    
    # Ask about preferences field
    print("\n2. USER PREFERENCES FIELD")
    print("-" * 30)
    preferences['include_preferences'] = input("Include user preferences JSON field? (y/n): ").lower().strip() == 'y'
    
    # Ask about UserProfile fields
    print("\n3. USER PROFILE FIELDS")
    print("-" * 30)
    
    profile_fields = {
        'job_title': 'Include job title field?',
        'social_links': 'Include social media links field?',
        'communication_preferences': 'Include communication preferences field?',
        'security_settings': 'Include security settings field?'
    }
    
    for field, question in profile_fields.items():
        preferences[field] = input(f"{question} (y/n): ").lower().strip() == 'y'
    
    return preferences

def generate_user_model(preferences):
    """
    Generate customized user model based on preferences
    """
    
    # Base imports
    model_content = """from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
import datetime
from django.utils import timezone as tz


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('first_name', extra_fields.get('first_name', ''))
        extra_fields.setdefault('last_name', extra_fields.get('last_name', ''))
        extra_fields.setdefault('time_zone', 'UTC')"""
    
    # Add preferences default if included
    if preferences.get('include_preferences', True):
        model_content += """
        extra_fields.setdefault('preferences', {
            'theme': 'dark',
            'notifications': {'email': True, 'push': False}
        })"""
    
    model_content += """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


"""
    
    # Add Role classes if roles are used
    if preferences.get('use_roles', True):
        # Start with default roles
        roles = ['ADMIN = \'Admin\', \'Admin\'', 'USER = \'User\', \'User\'']
        
        # Add custom roles
        custom_roles = preferences.get('custom_roles', [])
        for role in custom_roles:
            role_upper = role.upper().replace(' ', '_')
            roles.append(f"{role_upper} = '{role}', '{role}'")
        
        model_content += """class Role(models.TextChoices):
    """ + '\n    '.join(roles) + """


class RoleModel(models.Model):
    name = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=tz.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


"""
    
    # User model
    model_content += """class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)"""
    
    # Add role field if roles are used
    if preferences.get('use_roles', True):
        model_content += """
    role = models.ForeignKey(
        RoleModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="User Role"
    )"""
    
    model_content += """
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    time_zone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="UTC",
        verbose_name="Timezone",
        help_text="e.g., Ensures time-sensitive features align with user's local time."
    )"""
    
    # Add preferences field if included
    if preferences.get('include_preferences', True):
        model_content += """
    preferences = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name="Preferences",
        help_text="JSON key-value pairs for user-specific settings."
    )"""
    
    model_content += """
    date_joined = models.DateTimeField(default=tz.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    @property
    def fullname(self):
        \"\"\"Dynamic property for full name\"\"\"
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def __str__(self):
        return self.email


"""
    
    # UserProfile model
    profile_fields = []
    
    if preferences.get('job_title', False):
        profile_fields.append("""    job_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Job Title"
    )""")
    
    profile_fields.append("""    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )""")
    
    if preferences.get('social_links', False):
        profile_fields.append("""    social_links = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name="Social Media Links",
        help_text="List of URLs: [{'name':'GitHub','url':'https://...'}, ...]"
    )""")
    
    if preferences.get('communication_preferences', False):
        profile_fields.append("""    communication_preferences = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name="Communication Preferences",
        help_text="e.g., {'allow_team_mentions': true, 'digest_frequency': 'daily'}"
    )""")
    
    if preferences.get('security_settings', False):
        profile_fields.append("""    security_settings = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name="Security Settings",
        help_text="e.g., {'2fa_enabled': true, 'login_alerts': true}"
    )""")
    
    # Only add UserProfile if there are additional fields
    if profile_fields:
        model_content += """class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
"""
        model_content += '\n'.join(profile_fields)
        model_content += """
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
"""
    
    return model_content

def create_models_file(app_name, preferences):
    """
    Create models.py file with customized user model
    """
    models_content = generate_user_model(preferences)
    
    # Write to models.py in the app directory
    models_path = Path(app_name) / 'models.py'
    
    try:
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(models_content)
        
        print(f"\n✅ Created customized models.py in {app_name}/ directory")
        
        # Show summary of customizations
        print("\n" + "="*50)
        print("MODEL CUSTOMIZATION SUMMARY")
        print("="*50)
        
        if preferences.get('use_roles', True):
            print("✅ Role system included")
            custom_roles = preferences.get('custom_roles', [])
            if custom_roles:
                print(f"   Custom roles: {', '.join(custom_roles)}")
            else:
                print("   Default roles: Admin, User")
        else:
            print("❌ Role system excluded")
        
        print(f"✅ Preferences field: {'Included' if preferences.get('include_preferences', True) else 'Excluded'}")
        
        profile_fields = ['job_title', 'social_links', 'communication_preferences', 'security_settings']
        included_fields = [field for field in profile_fields if preferences.get(field, False)]
        
        if included_fields:
            print(f"✅ UserProfile fields: {', '.join(included_fields)}")
        else:
            print("❌ No additional UserProfile fields included")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating models.py: {e}")
        return False

def customize_user_model(app_name):
    """
    Main function to customize user model
    """
    print("\n🎨 Starting User Model Customization...")
    
    # Get user preferences
    preferences = get_user_preferences()
    
    # Create the customized models file
    success = create_models_file(app_name, preferences)
    
    if success:
        print(f"\n🎉 User model customization completed successfully!")
        print(f"📁 Check {app_name}/models.py for your customized user model")
        return True
    else:
        print("\n❌ Failed to customize user model")
        return False

if __name__ == "__main__":
    # For testing purposes
    app_name = input("Enter app name: ").strip()
    customize_user_model(app_name)