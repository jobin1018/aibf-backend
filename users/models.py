from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class Event(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    start_date = models.DateField(default='2025-04-24')
    start_time = models.TimeField(default='09:00:00')
    end_date = models.DateField(default='2025-04-27')
    end_time = models.TimeField(default='17:00:00')
    venue = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or ''

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    no_of_adults = models.IntegerField(blank=True, null=True)
    no_of_children_9_13 = models.IntegerField(blank=True, null=True)
    no_of_children_3_8 = models.IntegerField(blank=True, null=True)
    additional_adults = models.TextField(max_length=500, blank=True, null=True)
    additional_kids_9_13 = models.TextField(max_length=500, blank=True, null=True)
    additional_kids_3_8 = models.TextField(max_length=500, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    selected_package = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.name} - {self.event.name}"