# ratings/templatetags/ratings_extras.py
from django import template
from ratings.models import Game # Import Game model to access choices

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Gets an item from a dictionary."""
    return dictionary.get(key)

@register.filter(name='getattribute')
def getattribute(value, arg):
    """Gets an attribute of an object."""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    return None

@register.filter(name='get_game_severity_display')
def get_game_severity_display(severity_code):
    """Gets the display name for a Game severity code."""
    return dict(Game.SEVERITY_CHOICES).get(severity_code, '?')