from django.core.management.base import BaseCommand
from shop.models import RestaurantInfo


class Command(BaseCommand):
    help = "Legt die Restaurantdaten an (mit Standardwerten), falls noch nicht vorhanden"

    def handle(self, *args, **opts):
        obj = RestaurantInfo.load()
        self.stdout.write(self.style.SUCCESS(f"Restaurantdaten bereit: {obj.name}"))
