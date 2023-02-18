import logging

from django import forms

from .models import Order

logger = logging.getLogger(__name__)


class AddToCardForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["session", "items"]
