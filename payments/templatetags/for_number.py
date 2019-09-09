from django import template
register = template.Library()

@register.filter
def to_range(number):
    return range(number)
