from .models import User

def currency_choices(request):
    """Add currency choices to all templates"""
    return {
        'all_currencies': dict(User.CURRENCY_CHOICES) if request.user.is_authenticated else {}
    }
