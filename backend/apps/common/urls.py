from django.urls import path
from django.urls import include

from .views import HealthView


urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("admin/auth/", include("apps.authx.urls")),
    path("", include("apps.categories.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.customers.urls")),
    path("", include("apps.behaviors.urls")),
    path("", include("apps.carts.urls")),
    path("", include("apps.recommendations.urls")),
    path("", include("apps.mall.urls")),
]
