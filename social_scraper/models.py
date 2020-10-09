from django.db import models


PLATFORM_CHOICES = (
    ('instagram', 'Instagram'),
    ('facebook', 'Facebook'),
)


class SocialSource(models.Model):
    active = models.BooleanField(
        default=True,
    )
    username = models.CharField(
        max_length=64,
    )
    platform = models.CharField(
        max_lenght=16,
        choices=PLATFORM_CHOICES
    )