from django.template import Library

register = Library()

@register.filter
def mission_time_format(seconds):
    print seconds
    days = seconds // 86400
    hours = seconds % 86400 // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    return '%02d %02d %02d %02d' % (days, hours, minutes, seconds)

