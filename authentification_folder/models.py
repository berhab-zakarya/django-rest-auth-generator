from django.db import models
from django.contrib.auth.models import BaseUserManager,PermissionsMixin, AbstractBaseUser
import datetime

from django.utils import timezone as tz 

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('first_name', extra_fields.get('first_name', ''))
        extra_fields.setdefault('last_name', extra_fields.get('last_name', ''))
        extra_fields.setdefault('time_zone', 'UTC')
        extra_fields.setdefault('preferences', {
            'theme': 'dark',
            'notifications': {'email': True, 'push': False}
        })
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class Role(models.TextChoices):
    OWNER = 'Owner', 'Owner'
    ADMIN = 'Admin', 'Admin'
    MEMBER = 'Member', 'Member'
    GUEST = 'Guest', 'Guest'

class RoleModel(models.Model):
    name = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=tz.now)
    updated_at = models.DateTimeField(auto_now=True)
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    fullname = str(first_name).capitalize() + " " + str(last_name).capitalize()
    role = models.ForeignKey(
        RoleModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="User Role"
    )
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
        verbose_name=("Timezone"),
        help_text=("e.g., Ensures time-sensitive features align with user's local time.")
    )
    
    preferences = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=("Preferences"),
        help_text=("JSON key-value pairs for user-specific settings.")
    )
    date_joined = models.DateTimeField(default=tz.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    @property
    def fullname(self):
        """Dynamic property for full name"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    def __str__(self):
        return self.email
    
    
# models.py
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    
    # Suggested fields
    job_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=("Job Title")
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=("Phone Number")
    )
    
    social_links = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name=("Social Media Links"),
        help_text=("List of URLs: [{'name':'GitHub','url':'https://...'}, ...]")
    )
    
    communication_preferences = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=("Communication Preferences"),
        help_text=("e.g., {'allow_team_mentions': true, 'digest_frequency': 'daily'}")
    )
    
    security_settings = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=("Security Settings"),
        help_text=("e.g., {'2fa_enabled': true, 'login_alerts': true}")
    )