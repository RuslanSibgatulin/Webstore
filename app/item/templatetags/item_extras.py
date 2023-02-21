from django import template
from django.conf import settings

register = template.Library()


@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def currency(value):
    return f"{value} {settings.STRIPE_CURRENCY}"
