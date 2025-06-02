from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand,CommandError
User = get_user_model()
from authentification.models import RoleModel
import getpass
class Command(BaseCommand):
    help = 'Create a superuser with custom fields for Real-Time Collaborative Workspace'

    def add_arguments(self, parser):
        parser.add_argument('--email', help="Superuser's email address")
        parser.add_argument('--first-name', help="Superuser's first name")
        parser.add_argument('--last-name', help="Superuser's last name")
        parser.add_argument('--noinput', action='store_true', 
        help='DO NOT prompt for input (use with --email)')
    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name'] or ''
        last_name = options['last_name'] or ''
        
        # Validate email
        if not email:
            if options['noinput']:
                raise CommandError("Email required with --noinput")
            email = input("Email address: ")
        
        # Get password
        password = None
        if options['noinput']:
            raise CommandError("Cannot create superuser without password prompt")
        else:
            password = getpass.getpass()
            password2 = getpass.getpass("Password (again): ")
            if password != password2:
                raise CommandError("Passwords don't match")
        
        # Get or create Owner role
        role, created = RoleModel.objects.get_or_create(
            name='Owner',
            defaults={'description': 'System Owner'}
        )
        
        # Create superuser
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                time_zone="UTC",
                preferences={
                    'theme': 'dark',
                    'notifications': {'email': True, 'push': False}
                }
            )
            self.stdout.write(self.style.SUCCESS(
                f"Superuser created successfully: {email}\n"
                f"ID: {user.id}\n"
                f"Temporary password: {password} (change immediately!)"
            ))
        except Exception as e:
            raise CommandError(f"Error creating superuser: {str(e)}")
        
        