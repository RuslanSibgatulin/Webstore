from django.urls import path

from .views import (AddToCartApiView, ItemDetailView, ItemListView,
                    OrderDetailView)

app_name = "items"

urlpatterns = [
    path("", ItemListView.as_view(), name="item-list"),
    path("<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("<int:pk>/addtocart/", AddToCartApiView.as_view(), name="add-to-cart"),
    path("cart/", OrderDetailView.as_view(), name="cart"),
]
