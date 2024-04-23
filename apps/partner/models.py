from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


User = get_user_model()


class Establishment(models.Model):
    """
    Represents an establishment model
    """
    name = models.CharField(max_length=255)
    location_char = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(
        blank=True, null=True, upload_to='establishment_logos/',
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return 'Establishment: ' + self.name
