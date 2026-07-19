from decimal import Decimal

from django import template

from orders.models import ExchangeRate

register = template.Library()


@register.filter
def bdt(price):
    try:
        rate = ExchangeRate.objects.get(currency="USD")
        return round(Decimal(price) * rate.rate, 2)
    except ExchangeRate.DoesNotExist:
        return price
