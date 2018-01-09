from django import template

register = template.Library()

@register.filter(name='strip_single_quotes')
def strip_single_quotes(quoted_string):
    """Filter to remove single quotes from template variables."""
    return quoted_string.replace("'", "")

@register.filter(name='percentage')
def percentage(part, whole):
    """Filter to calculate percentage."""
    try:
        return "%d%%" % ((float(part) / float(whole) * 100) - 100)
    except (ValueError, ZeroDivisionError):
        return ""
