from .utils import category_icon_html, profile_photo_url
from .models import User


def currency_choices(request):
    return {
        'all_currencies': dict(User.CURRENCY_CHOICES) if request.user.is_authenticated else {},
        'profile_photo_url': profile_photo_url(request.user) if getattr(request, 'user', None) else '',
        'category_icon': category_icon_html,
    }
