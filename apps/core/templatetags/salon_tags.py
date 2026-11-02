from django import template

register = template.Library()


@register.filter
def spaced(value) -> str:
    """12345678 -> '12 345 678' (o'zbekcha raqam formati)."""
    try:
        return f"{int(value):,}".replace(",", " ")
    except (TypeError, ValueError):
        return value


@register.filter
def to_uzs(price, rate) -> int:
    try:
        return int(price) * int(rate)
    except (TypeError, ValueError):
        return 0
