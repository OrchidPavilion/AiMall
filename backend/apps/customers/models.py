from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    age = models.IntegerField(null=True, blank=True)
    hobby = models.CharField(max_length=255, blank=True, default="")
    address = models.CharField(max_length=500, blank=True, default="")
    avatar = models.CharField(max_length=500, blank=True, default="")
    password_hash = models.CharField(max_length=255, blank=True, default="")
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}({self.phone})"

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password(raw_password, self.password_hash)
