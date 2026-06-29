import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Legt einen Admin-Zugang an (falls noch keiner existiert)"

    def handle(self, *args, **opts):
        username = os.environ.get("ADMIN_USER", "admin")
        email = os.environ.get("ADMIN_EMAIL", "order@cardanokebapizza.at")
        password = os.environ.get("ADMIN_PASSWORD", "CardanoAdmin#2026")
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Admin '{username}' existiert bereits.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"Admin angelegt: Benutzer '{username}' / Passwort '{password}'  "
            f"-> BITTE NACH DEM ERSTEN LOGIN AENDERN."))
