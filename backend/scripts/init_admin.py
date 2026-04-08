import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
password = '123456'

user, created = User.objects.get_or_create(username=username, defaults={'is_staff': True, 'is_superuser': True})
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()
print('created' if created else 'updated', username)
