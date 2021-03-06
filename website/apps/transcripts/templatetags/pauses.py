from django.template import Library

register = Library()

@register.simple_tag
def pause_class(seconds):
    if 120 <= seconds < 300:
        return 'pause short'
    elif 300 <= seconds < 1800:
        return 'pause medium'
    elif 1800 <= seconds < 3600:
        return 'pause long'
    else:
        return ''

@register.simple_tag
def pause_length(seconds):
    hours = seconds // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    
    return '%d:%02d:%02d' % (hours, minutes, seconds)
