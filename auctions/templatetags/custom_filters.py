from django import template
import datetime

register = template.Library()

@register.filter
def timedelta_format(value):
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
