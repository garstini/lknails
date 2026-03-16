from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def euro(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return value
    formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} €"


@register.filter
def get_item(mapping, key):
    if not mapping:
        return []
    return mapping.get(key, [])
