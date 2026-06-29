from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from .models import Category, MenuItem, Order, OrderItem

Q = Decimal("0.01")


def q(v):
    return Decimal(v).quantize(Q, rounding=ROUND_HALF_UP)


class MenuItemSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ("id", "number", "name", "description", "price", "tax_rate",
                  "image_url", "tags", "available")

    def get_tags(self, obj):
        return obj.tag_list


class CategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("slug", "name", "subtitle", "items")

    def get_items(self, obj):
        items = obj.items.filter(available=True)
        return MenuItemSerializer(items, many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("name", "quantity", "unit_price", "tax_rate", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    mode_display = serializers.CharField(source="get_mode_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    address = serializers.CharField(source="address_line", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "number", "created_at", "status", "status_display", "mode",
                  "mode_display", "customer_name", "phone", "email", "address",
                  "wish_time", "note", "payment", "subtotal", "delivery_fee",
                  "tip", "vat_10", "vat_20", "total", "items")


class OrderCreateSerializer(serializers.Serializer):
    """Nimmt Positionen + Kundendaten an und berechnet die Summen serverseitig."""
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    mode = serializers.ChoiceField(choices=["delivery", "pickup"], default="delivery")
    customer_name = serializers.CharField(max_length=160)
    phone = serializers.CharField(max_length=40)
    email = serializers.EmailField(required=False, allow_blank=True)
    street = serializers.CharField(max_length=160, required=False, allow_blank=True)
    house_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    stair = serializers.CharField(max_length=20, required=False, allow_blank=True)
    door = serializers.CharField(max_length=20, required=False, allow_blank=True)
    zip = serializers.CharField(max_length=12, required=False, allow_blank=True)
    city = serializers.CharField(max_length=80, required=False, allow_blank=True)
    wish_time = serializers.CharField(max_length=40, required=False, allow_blank=True)
    note = serializers.CharField(max_length=300, required=False, allow_blank=True)
    payment = serializers.CharField(max_length=40, required=False, allow_blank=True)
    tip = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, default=0)

    FREE_FROM = Decimal("20")
    DELIVERY_FEE = Decimal("2.90")

    def create(self, validated):
        from .models import RestaurantInfo
        info = RestaurantInfo.load()
        free_from = info.free_delivery_from
        delivery_fee = info.delivery_fee
        lines = []
        subtotal = Decimal("0")
        vat10 = Decimal("0")
        vat20 = Decimal("0")

        for raw in validated["items"]:
            qty = int(raw.get("quantity", 1))
            if qty <= 0:
                continue
            item = None
            if raw.get("id"):
                item = MenuItem.objects.filter(pk=raw["id"]).first()
            if item:
                name, price, rate = item.name, item.price, item.tax_rate
            else:  # Fallback auf mitgesendete Werte
                name = raw.get("name", "Artikel")
                price = q(raw.get("price", 0))
                rate = int(raw.get("tax_rate", 10))
            line = q(price * qty)
            subtotal += line
            if rate == 20:
                vat20 += line * Decimal("0.20") / Decimal("1.20")
            else:
                vat10 += line * Decimal("0.10") / Decimal("1.10")
            lines.append(dict(name=name, quantity=qty, unit_price=price, tax_rate=rate))

        mode = validated["mode"]
        delivery = Decimal("0")
        if mode == "delivery" and subtotal > 0 and subtotal < free_from:
            delivery = delivery_fee
        tip = q(validated.get("tip") or 0) if mode == "delivery" else Decimal("0")
        total = q(subtotal + delivery + tip)

        user = None
        req = self.context.get("request")
        if req and req.user and req.user.is_authenticated:
            user = req.user

        order = Order.objects.create(
            user=user,
            customer_name=validated["customer_name"], phone=validated["phone"],
            email=validated.get("email", ""), mode=mode,
            street=validated.get("street", ""), house_no=validated.get("house_no", ""),
            stair=validated.get("stair", ""), door=validated.get("door", ""),
            zip=validated.get("zip", ""), city=validated.get("city", ""),
            wish_time=validated.get("wish_time", ""), note=validated.get("note", ""),
            payment=validated.get("payment", ""),
            subtotal=q(subtotal), delivery_fee=delivery, tip=tip, total=total,
            vat_10=q(vat10), vat_20=q(vat20),
        )
        for ln in lines:
            OrderItem.objects.create(order=order, **ln)
        return order


from .models import RestaurantInfo


class RestaurantInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantInfo
        exclude = ("id", "stripe_secret_key")


class MenuItemAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "category", "number", "name", "description", "price",
                  "tax_rate", "image_url", "tags", "available", "sort")


class CategoryAdminSerializer(serializers.ModelSerializer):
    items = MenuItemAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "slug", "name", "subtitle", "sort", "active", "items")
