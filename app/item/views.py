import logging
from typing import Any, Dict

from django.conf import settings
from django.db.models import F, Sum
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest,
                         JsonResponse)
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView, DetailView

from .forms import AddToCardForm
from .models import Item, ItemsInOrder, Order, OrderStatus
from .services.stripe import StripePayment
from .utils.utils import create_session

logger = logging.getLogger(__name__)


class ItemListView(ListView):
    template_name = "item/item_list.html"
    context_object_name = "items"
    model = Item
    paginate_by = 10
    ordering = ["name"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        create_session(request)
        return super().get(request, *args, **kwargs)


class ItemDetailView(DetailView):
    model = Item
    context_object_name = "item"
    template_name = "item/item_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["STRIPE_PUBLIC"] = settings.STRIPE_PUBLIC
        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        create_session(request)
        return super().get(request, *args, **kwargs)


class AddToCartApiView(BaseDetailView):
    model = Item
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        item = self.get_object()
        data = {
            "session": request.session.session_key,
            "items": [item]
        }
        form = AddToCardForm(request.POST | data)
        if form.is_valid():
            order, created = Order.objects.get_or_create(
                session=form.cleaned_data["session"],
                status=OrderStatus.CREATED
            )
            logger.debug("%s created %s", order, created)
            order.items.add(item)
            cart = {
                "cart":
                    {
                        "order": order.pk,
                        "items_count": order.items.count(),
                    }
            }
            return JsonResponse(cart)

        errors = form.errors.as_text()
        logger.error(errors)
        return HttpResponseBadRequest(errors)


class OrderDetailView(DetailView, StripePayment):
    model = Order
    context_object_name = "order"
    template_name = "order/order_detail.html"

    def get_object(self) -> Order:
        if self.request.session.session_key:
            order, created = Order.objects.annotate(
                amount=Sum(F("items__price") * F("itemsinorder__quantity"))
            ).get_or_create(
                session=self.request.session.session_key,
                status=OrderStatus.CREATED
            )
            return order
        return None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        order = self.object
        context = super().get_context_data(**kwargs)
        cart_items = ItemsInOrder.objects.filter(
            order=order
        ).values(
            name=F("item__name"),
            price=F("item__price"),
            sum=F("item__price") * F("quantity"),
        )
        context["cart"] = cart_items.values()
        context["STRIPE_PUBLIC"] = settings.STRIPE_PUBLIC
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        order = self.get_object()
        price_data = self.stripe_price(
            name=f"Order #{order.pk}",
            amount=order.amount,
            currency="rub"
        )
        json_session = {
            "session": self.create_checkout_session(price_data)
        }
        return JsonResponse(json_session)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        order = self.get_object()
        deleted, obj = ItemsInOrder.objects.filter(order=order).delete()
        logger.debug("%s cleared with. %s items deleted", order, deleted)
        return JsonResponse({"cleared": deleted})


class ItemBuyApiView(BaseDetailView, StripePayment):
    model = Item
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        item = self.get_object()
        price_data = self.stripe_price(
            item.name,
            item.price,
            item.description,
            "rub",
        )
        session = self.create_checkout_session(price_data)
        return JsonResponse({"session": session})
