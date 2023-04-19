from django import template

register = template.Library()

def split(value, delimiter=' '):
    return value.split(delimiter)

register.filter('split', split)