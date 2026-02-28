import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Library_with_DRF.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username= os.environ.get('SuperUser_Username'),
        email=os.environ.get('SuperUser_Email'),
        password=os.environ.get("SuperUser_Password") 
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
