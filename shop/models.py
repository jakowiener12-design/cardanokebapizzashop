from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    slug = models.SlugField("Kennung", max_length=60, unique=True)
    name = models.CharField("Name", max_length=120)
    subtitle = models.CharField("Untertitel", max_length=200, blank=True)
    sort = models.PositiveIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"
        ordering = ["sort", "name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    TAX_CHOICES = [(10, "10 % (Speisen / Ayran)"), (20, "20 % (Getränke)")]

    category = models.ForeignKey(Category, verbose_name="Kategorie",
                                 related_name="items", on_delete=models.CASCADE)
    number = models.PositiveIntegerField("Artikelnummer", null=True, blank=True)
    name = models.CharField("Name", max_length=160)
    description = models.CharField("Beschreibung", max_length=300, blank=True)
    price = models.DecimalField("Preis (Euro, brutto)", max_digits=7, decimal_places=2)
    tax_rate = models.PositiveIntegerField("Steuersatz", choices=TAX_CHOICES, default=10)
    image_url = models.URLField("Bild-URL", blank=True)
    tags = models.CharField("Tags (Komma)", max_length=120, blank=True,
                            help_text="z. B. pop, veg, vegan, spicy")
    available = models.BooleanField("Verfuegbar", default=True)
    sort = models.PositiveIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Menue-Artikel"
        verbose_name_plural = "Menue-Artikel"
        ordering = ["category__sort", "sort", "number", "name"]

    def __str__(self):
        return f"{self.name} ({self.price} Euro)"

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Order(models.Model):
    MODE_CHOICES = [("delivery", "Lieferung"), ("pickup", "Abholung")]
    STATUS_CHOICES = [
        ("new", "Neu"), ("confirmed", "Bestaetigt"), ("preparing", "In Zubereitung"),
        ("ready", "Fertig"), ("delivering", "In Lieferung"),
        ("done", "Abgeschlossen"), ("cancelled", "Storniert"),
    ]

    number = models.CharField("Bestellnummer", max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField("Eingegangen am", default=timezone.now)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="new")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Konto", null=True,
                             blank=True, on_delete=models.SET_NULL, related_name="orders")
    customer_name = models.CharField("Name", max_length=160)
    phone = models.CharField("Telefon", max_length=40)
    email = models.EmailField("E-Mail", blank=True)

    mode = models.CharField("Art", max_length=10, choices=MODE_CHOICES, default="delivery")
    street = models.CharField("Strasse", max_length=160, blank=True)
    house_no = models.CharField("Hausnr.", max_length=20, blank=True)
    stair = models.CharField("Stiege", max_length=20, blank=True)
    door = models.CharField("Tuer", max_length=20, blank=True)
    zip = models.CharField("PLZ", max_length=12, blank=True)
    city = models.CharField("Ort", max_length=80, blank=True)

    wish_time = models.CharField("Wunschzeit", max_length=40, blank=True)
    note = models.CharField("Anmerkung", max_length=300, blank=True)
    payment = models.CharField("Zahlung", max_length=40, blank=True)

    subtotal = models.DecimalField("Zwischensumme", max_digits=8, decimal_places=2, default=0)
    delivery_fee = models.DecimalField("Liefergebuehr", max_digits=6, decimal_places=2, default=0)
    tip = models.DecimalField("Trinkgeld", max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField("Gesamt", max_digits=8, decimal_places=2, default=0)
    vat_10 = models.DecimalField("enth. MwSt. 10 %", max_digits=8, decimal_places=2, default=0)
    vat_20 = models.DecimalField("enth. MwSt. 20 %", max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} - {self.customer_name} - {self.total} Euro"

    @property
    def address_line(self):
        if self.mode != "delivery":
            return "Abholung im Lokal"
        parts = f"{self.street} {self.house_no}".strip()
        extra = " ".join(x for x in [self.stair and f"Stiege {self.stair}",
                                     self.door and f"Tuer {self.door}"] if x)
        loc = f"{self.zip} {self.city}".strip()
        return ", ".join(p for p in [parts, extra, loc] if p)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._make_number()
        super().save(*args, **kwargs)

    def _make_number(self):
        today = timezone.localdate()
        prefix = today.strftime("C-%y%m%d-")
        last = Order.objects.filter(number__startswith=prefix).order_by("-number").first()
        seq = (int(last.number.split("-")[-1]) + 1) if last else 1
        return f"{prefix}{seq:03d}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    name = models.CharField("Artikel", max_length=200)
    quantity = models.PositiveIntegerField("Menge", default=1)
    unit_price = models.DecimalField("Einzelpreis", max_digits=7, decimal_places=2)
    tax_rate = models.PositiveIntegerField("Steuersatz", default=10)

    class Meta:
        verbose_name = "Bestellposition"
        verbose_name_plural = "Bestellpositionen"

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class RestaurantInfo(models.Model):
    """Zentrale Restaurantdaten (nur ein Datensatz). Steuert Beleg, Shop und Landing."""
    name = models.CharField("Name", max_length=120, default="Cardano Kebapizza e.U.")
    owner = models.CharField("Inhaber", max_length=120, blank=True)
    street = models.CharField("Strasse", max_length=160, default="Etrichstraße 40/2/10A")
    zip = models.CharField("PLZ", max_length=12, default="1110")
    city = models.CharField("Ort", max_length=80, default="Wien")
    uid = models.CharField("UID", max_length=30, default="ATU77114908")
    fn = models.CharField("Firmenbuch", max_length=30, default="FN 610587y")
    gisa = models.CharField("GISA", max_length=30, default="34005309")
    phone = models.CharField("Telefon (Anzeige)", max_length=40, default="+43 1 9258149")
    phone_tel = models.CharField("Telefon (Wahl-Link)", max_length=40, default="+4319258149")
    email = models.EmailField("E-Mail", default="order@cardanokebapizza.at")
    hours = models.CharField("Oeffnungszeiten", max_length=120, default="Täglich 11:00 – 23:00")
    payment = models.CharField("Zahlung", max_length=160, default="Bar, Karte, Pluxee, Edenred")
    delivery_fee = models.DecimalField("Liefergebuehr (Euro)", max_digits=6, decimal_places=2, default=2.90)
    free_delivery_from = models.DecimalField("Gratis Lieferung ab (Euro)", max_digits=6, decimal_places=2, default=20.00)
    instagram = models.URLField("Instagram", blank=True, default="https://www.instagram.com/cardanokebapizza/")
    facebook = models.URLField("Facebook", blank=True, default="https://www.facebook.com/p/Cardano-Kebapizza-61552703820637/")
    tiktok = models.URLField("TikTok", blank=True, default="https://www.tiktok.com/@cardano.kebapizza")
    whatsapp = models.URLField("WhatsApp", blank=True, default="https://wa.me/4319258149")
    online_payment = models.BooleanField("Online-Zahlung aktiv", default=False)
    payment_provider = models.CharField("Anbieter", max_length=30, blank=True, default="stripe")
    stripe_publishable_key = models.CharField("Stripe Publishable Key", max_length=200, blank=True)
    stripe_secret_key = models.CharField("Stripe Secret Key", max_length=200, blank=True)

    class Meta:
        verbose_name = "Restaurantdaten"
        verbose_name_plural = "Restaurantdaten"

    def __str__(self):
        return "Restaurantdaten"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
