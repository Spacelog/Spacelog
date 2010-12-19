from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@stringfilter
@register.filter
def nbspify(value):
    return mark_safe('&nbsp;'.join(conditional_escape(s) for s in value.split(' ')))

