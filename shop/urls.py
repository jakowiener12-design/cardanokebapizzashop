from django.urls import path
from . import views, admin_api

urlpatterns = [
    path("menu/", views.menu, name="menu"),
    path("info/", views.info, name="info"),
    path("orders/", views.create_order, name="create_order"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("my-orders/", views.my_orders, name="my_orders"),
    # Admin-Dashboard-API (nur fuer Staff)
    path("admin/orders/", admin_api.orders),
    path("admin/orders/<int:pk>/", admin_api.order_detail),
    path("admin/menu/", admin_api.menu),
    path("admin/categories/", admin_api.category_create),
    path("admin/categories/<int:pk>/", admin_api.category_detail),
    path("admin/items/", admin_api.item_create),
    path("admin/items/<int:pk>/", admin_api.item_detail),
    path("admin/info/", admin_api.info),
    path("admin/revenue/", admin_api.revenue),
]
