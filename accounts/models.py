from django.contrib.auth.models import AbstractUser
from django.db import models

ACCOUNT_CHOICES = [
    ('personal', 'Personal'),
    ('business', 'Business'),
]

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    mobile_no = models.CharField(max_length=15)
    address = models.TextField()
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES)

    def __str__(self):
        return self.username
