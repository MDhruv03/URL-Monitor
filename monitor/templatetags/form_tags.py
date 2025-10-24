from django import template

register = template.Library()

@register.filter
def widget_type(field):
    """Get the widget class name for a form field"""
    return field.field.widget.__class__.__name__
