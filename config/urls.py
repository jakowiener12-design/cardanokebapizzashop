from pathlib import Path
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include
from django.views.static import serve as static_serve

FRONTEND = Path(settings.BASE_DIR) / "frontend"


def manage(request):
    return static_serve(request, "manage.html", document_root=str(FRONTEND))


def home(request):
    # Startseite des Shops
    return static_serve(request, "index.html", document_root=str(FRONTEND))


urlpatterns = [
    path("admin/", admin.site.urls),          # Admin-Panel
    path("api/", include("shop.urls")),        # API fuer den Shop
    path("manage/", manage),                   # eigenes Admin-Dashboard
    path("", home),                            # Startseite
    re_path(r"^(?P<path>.+\.(?:html|css|js|png|jpg|jpeg|svg|ico|webp|gif))$",
            static_serve, {"document_root": str(FRONTEND)}),  # restliche Shop-Dateien
]
