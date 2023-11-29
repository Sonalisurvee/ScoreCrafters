from django import template
import math

register = template.Library()

@register.filter
def valid_value(value):
    if value is None or math.isnan(value) or value == 0 or math.isinf(value):
        return False
    return True
