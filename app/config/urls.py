from django.contrib import admin
from django.urls import include, path
from item.views import ItemBuyApiView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("items/", include("item.urls", namespace="items")),
    path("buy/<int:pk>/", ItemBuyApiView.as_view()),
]
