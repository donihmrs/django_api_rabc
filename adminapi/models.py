from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_STAFF, 'Staff'),
    ]


    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN


    def is_manager(self):
        return self.role == self.ROLE_MANAGER


    def is_staff_role(self):
        return self.role == self.ROLE_STAFF

class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Invitation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=3)
        super().save(*args, **kwargs)


    def is_valid(self):
        return (not self.is_used) and (self.expires_at is None or timezone.now() < self.expires_at)