from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, Order, OrderItem


admin.site.site_header = "Cardano Kebapizza - Verwaltung"
admin.site.site_title = "Cardano Admin"
admin.site.index_title = "Shop verwalten"


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ("number", "name", "price", "tax_rate", "available", "sort")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "item_count", "sort", "active")
    list_editable = ("sort", "active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MenuItemInline]

    @admin.display(description="Artikel")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "number", "price", "tax_rate", "available", "sort")
    list_editable = ("price", "tax_rate", "available", "sort")
    list_filter = ("category", "tax_rate", "available")
    search_fields = ("name", "description", "number")
    list_per_page = 50


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "quantity", "unit_price", "tax_rate", "line_total")
    can_delete = False

    @admin.display(description="Summe")
    def line_total(self, obj):
        return f"{obj.line_total:.2f} Euro"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "created_at", "customer_name", "mode_badge",
                    "total_eur", "wish_time", "status")
    list_filter = ("status", "mode", "created_at")
    search_fields = ("number", "customer_name", "phone", "email")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    list_per_page = 40
    readonly_fields = ("number", "created_at", "address_block", "totals_block",
                       "customer_name", "phone", "email", "mode", "wish_time",
                       "note", "payment", "subtotal", "delivery_fee", "tip",
                       "vat_10", "vat_20", "total", "street", "house_no", "stair",
                       "door", "zip", "city", "user")
    fieldsets = (
        ("Bestellung", {"fields": ("number", "created_at", "status", "mode", "wish_time")}),
        ("Kunde", {"fields": ("user", "customer_name", "phone", "email", "address_block", "note")}),
        ("Betrag", {"fields": ("totals_block",)}),
    )

    @admin.display(description="Art")
    def mode_badge(self, obj):
        color = "#1f7a4d" if obj.mode == "delivery" else "#a08a4f"
        return format_html('<b style="color:{}">{}</b>', color, obj.get_mode_display())

    @admin.display(description="Gesamt", ordering="total")
    def total_eur(self, obj):
        return f"{obj.total:.2f} Euro"

    @admin.display(description="Lieferadresse")
    def address_block(self, obj):
        return obj.address_line

    @admin.display(description="Abrechnung")
    def totals_block(self, obj):
        return format_html(
            "Zwischensumme: {} Euro<br>Liefergebuehr: {} Euro<br>Trinkgeld: {} Euro<br>"
            "<b>Gesamt: {} Euro</b><br><small>enthalten: 10% = {} Euro &nbsp; 20% = {} Euro</small>",
            f"{obj.subtotal:.2f}", f"{obj.delivery_fee:.2f}", f"{obj.tip:.2f}",
            f"{obj.total:.2f}", f"{obj.vat_10:.2f}", f"{obj.vat_20:.2f}")


from .models import RestaurantInfo


@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Betrieb", {"fields": ("name", "owner", "street", "zip", "city")}),
        ("Rechtliches", {"fields": ("uid", "fn", "gisa")}),
        ("Kontakt", {"fields": ("phone", "phone_tel", "email", "hours", "payment")}),
        ("Lieferung", {"fields": ("delivery_fee", "free_delivery_from")}),
        ("Social Media", {"fields": ("instagram", "facebook", "tiktok", "whatsapp")}),
    )

    def has_add_permission(self, request):
        return not RestaurantInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
