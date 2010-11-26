from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.filter
def summarise(result, field):
    return mark_safe(result.summarise(field, maxlen=100, ellipsis='&hellip;', hl=('<em>', '</em>')))
