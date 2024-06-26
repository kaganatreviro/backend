from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.gis.db import models as geomodels
from django.utils import timezone

from apps.partner.managers import EstablishmentManager

User = get_user_model()


class Establishment(models.Model):
    """
    Represents an establishment model
    """

    name = models.CharField(max_length=255)
    location = geomodels.PointField(geography=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    logo = models.ImageField(
        blank=True,
        null=True,
        upload_to="establishment_logos/",
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    happyhours_start = models.TimeField( blank=True)
    happyhours_end = models.TimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    objects = EstablishmentManager()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
            models.Index(name='location_gist', fields=['location'], opclasses=['gist'])
        ]

    def __str__(self):
        return "Establishment: " + self.name

    def is_happy_hour(self):
        now = timezone.localtime().time()
        return self.happyhours_start <= now <= self.happyhours_end
