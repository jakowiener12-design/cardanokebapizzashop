import json
from pathlib import Path
from django.core.management.base import BaseCommand
from shop.models import Category, MenuItem


class Command(BaseCommand):
    help = "Importiert das Menue aus shop/menu_seed.json"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Vorhandene Kategorien/Artikel zuerst loeschen")

    def handle(self, *args, **opts):
        path = Path(__file__).resolve().parent.parent.parent / "menu_seed.json"
        data = json.loads(path.read_text(encoding="utf-8"))

        if opts["reset"]:
            MenuItem.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Bestehendes Menue geloescht.")

        ncat = nit = 0
        for c in data:
            cat, _ = Category.objects.update_or_create(
                slug=c["slug"],
                defaults=dict(name=c["name"], subtitle=c.get("subtitle", ""),
                              sort=c.get("sort", 0), active=True))
            ncat += 1
            for it in c["items"]:
                MenuItem.objects.update_or_create(
                    category=cat, name=it["name"],
                    defaults=dict(number=it.get("number"), description=it.get("description", ""),
                                  price=it["price"], tax_rate=it["tax_rate"],
                                  image_url=it.get("image_url", ""), tags=it.get("tags", ""),
                                  sort=it.get("sort", 0), available=True))
                nit += 1
        self.stdout.write(self.style.SUCCESS(f"Import fertig: {ncat} Kategorien, {nit} Artikel."))
