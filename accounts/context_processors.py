from .utils import CURRENCY_SYMBOLS, category_icon_html, profile_photo_url
from .models import User


def currency_choices(request):
    user = getattr(request, 'user', None)
    authenticated = bool(user and getattr(user, 'is_authenticated', False))
    code = getattr(user, 'preferred_currency', 'GHS') if authenticated else 'GHS'
    return {
        'all_currencies': dict(User.CURRENCY_CHOICES) if authenticated else {},
        'profile_photo_url': profile_photo_url(user) if authenticated else '',
        'currency_symbol': CURRENCY_SYMBOLS.get(code, '₵'),
        'category_icon': category_icon_html,
        'asset_v': '6',
    }
