from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from .models import Item


class ItemList(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            id=100,
            name="Test item",
            description="Test item description",
            price=20000
        )
        url = reverse("items:item-list")
        self.response = self.client.get(url)

    def test_list_template(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.response, "item/item_list.html")
        self.assertContains(self.response, "Items")
        self.assertContains(self.response, "Test item")
        self.assertContains(self.response, "200.00")


class ItemDetail(TestCase):
    def setUp(self):
        self.item_id = 100
        self.item_price = 10000
        self.item = Item.objects.create(
            id=self.item_id,
            name="Test item",
            description="Test item description",
            price=self.item_price
        )
        url = reverse("items:item-detail", args=[self.item_id])
        self.response = self.client.get(url)

    def test_item_detail_template(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.response, "item/item_detail.html")
        self.assertContains(self.response, "Test item")
        self.assertContains(self.response, str(self.item_price / 100))
        self.assertContains(self.response, "Buy now")
        self.assertContains(self.response, "Add to cart")

    def test_add_to_cart(self):
        url = reverse("items:add-to-cart", args=[self.item_id])
        self.response = self.client.post(url)

        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(self.response["content-type"], "application/json")

        cart = self.response.json()["cart"]
        self.assertEqual(cart["order"], 1)
        self.assertEqual(cart["items_count"], 1)

    def test_buy_now(self):
        """Stripe API test keys needs.
        """
        url = reverse("buy-now", args=[self.item_id])
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(self.response["content-type"], "application/json")
        session = self.response.json()["session"]
        self.assertEqual(session["amount_total"], self.item_price)
        self.assertEqual(session["status"], "open")


class TestCart(TestCase):
    def setUp(self):
        self.item_id = 100
        self.item_price = 10000
        self.item = Item.objects.create(
            id=self.item_id,
            name="Test item",
            description="Test item description",
            price=self.item_price
        )
        # Create session on item-list page
        self.response = self.client.get(reverse("items:item-list"))

        url = reverse("items:cart")
        self.response = self.client.get(url)

    def test_cart_template(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.response, "order/order_detail.html")
        self.assertContains(self.response, "Your cart")
        self.assertContains(self.response, "Item")
        self.assertContains(self.response, "Price")

    def test_add_to_cart_and_payment(self):
        """Stripe API test keys needs.
        """
        url = reverse("items:add-to-cart", args=[self.item_id])
        self.response = self.client.post(url)

        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(self.response["content-type"], "application/json")

        cart = self.response.json()["cart"]
        self.assertEqual(cart["order"], 1)
        self.assertEqual(cart["items_count"], 1)

        url = reverse("items:cart")
        self.response = self.client.post(url)
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(self.response["content-type"], "application/json")
        session = self.response.json()["session"]
        self.assertEqual(session["amount_total"], self.item_price)
        self.assertEqual(session["status"], "open")
