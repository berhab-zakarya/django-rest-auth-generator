from django.db.models.signals import post_save
from django.dispatch import receiver

from authentification.models import User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
    
        UserProfile.objects.create(user=instance)
        print(f"User {instance.email} created with role {instance.role.name}")
    else:
        print(f"User {instance.email} updated")