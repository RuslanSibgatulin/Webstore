from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _


class Item(models.Model):
    name = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    price = models.PositiveIntegerField(_("Price"))

    def __str__(self) -> str:
        return f"{self.name}"


class OrderStatus(models.TextChoices):
    CREATED = "created", _("Created")
    PAYED = "payed", _("Payed")
    CANCELLED = "cancelled", _("Cancelled")


class Order(models.Model):
    session = models.CharField(
        _("Session"),
        max_length=40,
        db_index=True
    )
    items = models.ManyToManyField(
        Item,
        through="ItemsInOrder",
        verbose_name=_("Items")
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        editable=False,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED
    )

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    def __str__(self) -> str:
        return f"Order #{self.id}"

    @property
    def amount(self) -> int:
        return self.items.annotate(
            item_sum=F("price") * F("itemsinorder__quantity")
        ).aggregate(amount=Sum("item_sum"))["amount"]

    def payment_complete(self):
        if self.status == OrderStatus.CREATED:
            self.status = OrderStatus.PAYED
            self.save()


class ItemsInOrder(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(_("Quantity"), default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "order"],
                name="items_in_order_idx")
        ]
