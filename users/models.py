from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")
    role = models.CharField(max_length=20, blank=False, null=False,choices=[("admin","admin"),("user","user"),("controller","contoller")],default="user")

    USERNAME_FIELD = "username"   # e.g: "username", "email"
    EMAIL_FIELD = "email"         # e.g: "email", "primary_email"