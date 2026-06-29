from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Category, Order
from .serializers import (CategorySerializer, OrderSerializer,
                          OrderCreateSerializer)


@api_view(["GET"])
@permission_classes([AllowAny])
def menu(request):
    cats = Category.objects.filter(active=True).prefetch_related("items")
    return Response(CategorySerializer(cats, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_order(request):
    ser = OrderCreateSerializer(data=request.data, context={"request": request})
    ser.is_valid(raise_exception=True)
    order = ser.save()
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = (request.data.get("email") or "").strip().lower()
    name = (request.data.get("name") or "").strip()
    password = request.data.get("password") or ""
    if not email or not password:
        return Response({"detail": "E-Mail und Passwort erforderlich."},
                        status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=email).exists():
        return Response({"detail": "Konto existiert bereits."},
                        status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=email, email=email, password=password,
                                    first_name=name)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "name": name, "email": email})


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    user = authenticate(username=email, password=password)
    if not user:
        return Response({"detail": "E-Mail oder Passwort falsch."},
                        status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "name": user.first_name, "email": user.email, "is_staff": user.is_staff})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return Response(OrderSerializer(orders, many=True).data)


from .models import RestaurantInfo
from .serializers import RestaurantInfoSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def info(request):
    return Response(RestaurantInfoSerializer(RestaurantInfo.load()).data)
