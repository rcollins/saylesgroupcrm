"""Context processors for CRM app (app name, logo, choice labels)."""
from .choice_utils import get_choice_labels_dict
from .models import AppSettings


def app_settings(request):
    """Add app_name, logo_url, chart_colors, and inactivity_timeout_minutes to every template."""
    settings_obj = AppSettings.load()
    logo_url = settings_obj.logo.url if settings_obj.logo else None
    colors = settings_obj.chart_colors or {}
    inactivity_minutes = getattr(settings_obj, 'inactivity_timeout_minutes', 0) or 0
    return {
        'app_settings': {
            'app_name': settings_obj.app_name,
            'logo_url': logo_url,
            'chart_colors': colors,
            'inactivity_timeout_minutes': inactivity_minutes,
        },
    }


def choice_labels(request):
    """Add choice_labels dict for template display: choice_labels.client_status['active'] -> 'Active Client'."""
    return {'choice_labels': get_choice_labels_dict()}
