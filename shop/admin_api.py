from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status as http

from .models import Category, MenuItem, Order, RestaurantInfo
from .serializers import (OrderSerializer, MenuItemAdminSerializer,
                          CategoryAdminSerializer, RestaurantInfoSerializer)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def orders(request):
    qs = Order.objects.all().prefetch_related("items")
    st = request.GET.get("status")
    if st:
        qs = qs.filter(status=st)
    return Response(OrderSerializer(qs, many=True).data)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def order_detail(request, pk):
    try:
        o = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(status=http.HTTP_404_NOT_FOUND)
    if "status" in request.data:
        o.status = request.data["status"]
        o.save(update_fields=["status"])
    return Response(OrderSerializer(o).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def menu(request):
    cats = Category.objects.all().prefetch_related("items")
    return Response(CategoryAdminSerializer(cats, many=True).data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def category_create(request):
    data = request.data.copy()
    if not data.get("slug"):
        base = slugify(data.get("name", "kategorie")) or "kategorie"
        slug, i = base, 2
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"; i += 1
        data["slug"] = slug
    if data.get("sort") in (None, ""):
        data["sort"] = (Category.objects.count())
    ser = CategoryAdminSerializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data, status=http.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminUser])
def category_detail(request, pk):
    try:
        c = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=http.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        c.delete()
        return Response(status=http.HTTP_204_NO_CONTENT)
    ser = CategoryAdminSerializer(c, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def item_create(request):
    data = request.data.copy()
    if data.get("sort") in (None, ""):
        cat = data.get("category")
        data["sort"] = MenuItem.objects.filter(category_id=cat).count() if cat else 0
    ser = MenuItemAdminSerializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data, status=http.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminUser])
def item_detail(request, pk):
    try:
        it = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return Response(status=http.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        it.delete()
        return Response(status=http.HTTP_204_NO_CONTENT)
    ser = MenuItemAdminSerializer(it, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


@api_view(["GET", "PUT"])
@permission_classes([IsAdminUser])
def info(request):
    obj = RestaurantInfo.load()
    if request.method == "PUT":
        ser = RestaurantInfoSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        # Secret wird separat gesetzt (nie ausgeliefert)
        sk = request.data.get("stripe_secret_key")
        if sk:
            obj.stripe_secret_key = sk
            obj.save(update_fields=["stripe_secret_key"])
        out = RestaurantInfoSerializer(obj).data
        out["stripe_secret_set"] = bool(obj.stripe_secret_key)
        return Response(out)
    out = RestaurantInfoSerializer(obj).data
    out["stripe_secret_set"] = bool(obj.stripe_secret_key)
    return Response(out)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def revenue(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
    period = request.GET.get("period", "day")
    trunc = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth, "year": TruncYear}.get(period, TruncDay)
    qs = (Order.objects.exclude(status="cancelled")
          .annotate(p=trunc("created_at")).values("p")
          .annotate(count=Count("id"), total=Sum("total"),
                    vat10=Sum("vat_10"), vat20=Sum("vat_20"),
                    delivery=Sum("delivery_fee"), tip=Sum("tip"))
          .order_by("-p"))
    fmt = {"day": "%d.%m.%Y", "week": "KW %V / %G", "month": "%m.%Y", "year": "%Y"}.get(period, "%d.%m.%Y")
    rows = []
    g_total = g_v10 = g_v20 = g_net = g_count = 0
    for r in qs:
        total = float(r["total"] or 0); v10 = float(r["vat10"] or 0); v20 = float(r["vat20"] or 0)
        tip = float(r["tip"] or 0)
        net = total - v10 - v20 - tip
        rows.append({"period": r["p"].strftime(fmt), "count": r["count"],
                     "net": round(net, 2), "vat10": round(v10, 2), "vat20": round(v20, 2),
                     "tip": round(tip, 2), "total": round(total, 2)})
        g_total += total; g_v10 += v10; g_v20 += v20; g_net += net; g_count += r["count"]
    summary = {"count": g_count, "net": round(g_net, 2), "vat10": round(g_v10, 2),
               "vat20": round(g_v20, 2), "total": round(g_total, 2)}
    return Response({"period": period, "rows": rows, "summary": summary})
