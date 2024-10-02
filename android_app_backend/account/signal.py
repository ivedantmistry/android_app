from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from django.contrib.auth.signals import user_logged_in
from .models import User
from django.utils import timezone

@receiver(user_logged_in)
def update_last_login(sender, user, request, **kwargs):
    user.last_login = timezone.now()
    user.save()