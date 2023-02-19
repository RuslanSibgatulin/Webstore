import logging
from typing import Any, Dict

import stripe
from django.conf import settings
from django.db.models import F
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest,
                         JsonResponse)
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView, DetailView

from .forms import AddToCardForm
from .models import Item, ItemsInOrder, Order, OrderStatus
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


class OrderDetailView(DetailView):
    model = Order
    context_object_name = "order"
    template_name = "order/order_detail.html"

    def get_object(self) -> Order:
        if self.request.session.session_key:
            order, created = Order.objects.get_or_create(
                session=self.request.session.session_key,
                status=OrderStatus.CREATED
            )
            return order
        return None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        order = self.get_object()
        context = super().get_context_data(**kwargs)
        cart_items = ItemsInOrder.objects.filter(
            order=order
        ).values(
            name=F("item__name"),
            price=F("item__price"),
            amount=F("item__price") * F("quantity")
        )
        context["cart"] = cart_items.values()
        logger.debug(context)
        return context


class ItemBuyApiView(BaseDetailView):
    model = Item
    http_method_names = ["get"]

    def get_price_json(self) -> Dict:
        item = {
            "quantity": 1,
            "price_data": {
                "currency": "rub",
                "unit_amount": self.object.price,
                "product_data": {
                    "name": self.object.name,
                    "description": self.object.description or "No description",
                },
            },
        }
        return item

    def create_checkout_session(self) -> Any:
        try:
            success_url = self.request.META.get("HTTP_REFERER") + "?session_id={CHECKOUT_SESSION_ID}"

            checkout_session = stripe.checkout.Session.create(
                api_key=settings.STRIPE_SECRET,
                line_items=[self.get_price_json()],
                mode="payment",
                success_url=success_url,
                cancel_url=self.request.META.get("HTTP_REFERER"),
            )
        except Exception as err:
            logger.error("Create checkout session error: %s", err)
            return None

        logger.debug("Checkout session created: %s", checkout_session)
        return checkout_session

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        session = self.create_checkout_session()
        return {"session": session}

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
