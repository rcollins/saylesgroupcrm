"""Template filters for CRM app (e.g. US currency formatting)."""
from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """Look up key in dict d. Used for choice_labels[list_type][code]. Returns key if not found."""
    if d is None:
        return key
    return d.get(key, key)


@register.filter
def usd(value, decimals=0):
    """
    Format a number as US currency with commas (e.g. $1,234,567 or $1,234,567.00).
    Use decimals=0 for whole dollars, decimals=2 for cents: {{ price|usd:2 }}.
    Returns empty string if value is None.
    """
    if value is None:
        return ""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return ""
    d = 0 if decimals is None else int(decimals)
    if d == 0:
        return f"${num:,.0f}"
    return f"${num:,.{d}f}"
