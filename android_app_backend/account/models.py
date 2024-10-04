from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.crypto import get_random_string
from django.utils import timezone
from uuid import uuid4
import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **other_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        user = self.create_user(
            email = self.normalize_email(email),
            password=password,
            **other_fields
        )
        user.is_verified = True
        user.email_verified = True
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    STATUS = (
        ('active', 'active'),
        ('suspended', 'suspended'),
        ('deactivated', 'deactivated')
    )
    email = models.EmailField(blank=False, unique=True)
    AVATAR_URL = 'https://res.cloudinary.com/ddl2pf4qh/image/upload/v1629388876/fintrak/FinProfile_no9nb1.png'
    avatar = models.URLField(default=AVATAR_URL)
    phone_number = models.CharField(max_length=20)
    username = models.CharField(max_length=255, unique=False, blank=True)
    uuid = models.UUIDField(default=uuid4, editable=False)
    email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS, max_length=20)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f'{self.email}'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class OTP(models.Model):
    EVENT_CHOICES = (
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
    )

    # Generic foreign key to allow linking to either Seller or Buyer or other models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = GenericForeignKey('content_type', 'object_id')

    otp_code = models.CharField(max_length=6)
    event = models.CharField(choices=EVENT_CHOICES, max_length=50)  # Type of event that triggered OTP
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # OTP expiry time
    is_used = models.BooleanField(default=False)
    otp_id = models.UUIDField(default=uuid4, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Set expiry time to 5 minutes from now if not already set
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=5)
        super().save(*args, **kwargs)

    def has_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.user} - {self.event}"
