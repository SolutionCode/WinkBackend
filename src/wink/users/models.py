from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, password=None, **kwargs):
        user = self.model(**kwargs)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_admin = True
        user.save()
        return user


def validate_handle(value):
    if value[0] != '@':
        raise ValidationError('Handle needs to start with @')


class User(AbstractBaseUser):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    phone_number = models.CharField(max_length=32, null=True, blank=True)

    handle = models.CharField(max_length=32, unique=True, validators=[validate_handle])
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    date_of_birth = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['handle']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin