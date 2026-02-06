"""Helpers for dynamic choice lists (Application Admin)."""
from django.core.cache import cache

CACHE_KEY_CHOICES = 'crm_choice_lists'
CACHE_TIMEOUT = 300  # 5 minutes


def get_choices_for_list(list_type):
    """Return list of (code, label) for a list_type, ordered. Used by forms."""
    cache_key = f'{CACHE_KEY_CHOICES}_{list_type}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    from .models import ChoiceList
    choices = list(
        ChoiceList.objects.filter(list_type=list_type).order_by('order', 'label').values_list('code', 'label')
    )
    cache.set(cache_key, choices, CACHE_TIMEOUT)
    return choices


def get_choice_labels_dict():
    """Return dict of list_type -> {code: label} for template display. Used by context processor."""
    cached = cache.get(CACHE_KEY_CHOICES)
    if cached is not None:
        return cached
    from .models import ChoiceList
    from collections import defaultdict
    d = defaultdict(dict)
    for row in ChoiceList.objects.order_by('order', 'label').values_list('list_type', 'code', 'label'):
        d[row[0]][row[1]] = row[2]
    result = dict(d)
    cache.set(CACHE_KEY_CHOICES, result, CACHE_TIMEOUT)
    return result


def invalidate_choice_cache(list_type=None):
    """Call after ChoiceList or AppSettings change so forms/templates see new data."""
    if list_type:
        cache.delete(f'{CACHE_KEY_CHOICES}_{list_type}')
    cache.delete(CACHE_KEY_CHOICES)
