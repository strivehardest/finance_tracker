from django import template
from accounts.utils import category_icon_html, normalize_icon, profile_photo_url

register = template.Library()


@register.simple_tag
def cat_icon(category):
    if not category:
        return ''
    return category_icon_html(getattr(category, 'icon', ''), getattr(category, 'color', '#f57c00'))


@register.simple_tag
def cat_icon_code(icon, color='#f57c00'):
    return category_icon_html(icon, color)


@register.filter
def as_fa_icon(icon):
    return normalize_icon(icon)


@register.simple_tag
def user_photo(user):
    return profile_photo_url(user)
