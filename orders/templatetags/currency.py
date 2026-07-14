from decimal import Decimal

from django import template

from orders.models import ExchangeRate

register = template.Library()


@register.filter
def bdt(price):

    try:

        rate = ExchangeRate.objects.get(
            currency="USD",
        )

        return round(
            Decimal(price) * rate.rate,
            2,
        )

    except ExchangeRate.DoesNotExist:

        return price


@register.simple_tag
def exchange_rate():

    try:

        return ExchangeRate.objects.get(
            currency="USD",
        ).rate

    except ExchangeRate.DoesNotExist:

        return Decimal("0")