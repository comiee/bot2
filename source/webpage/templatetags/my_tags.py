from django import template

register = template.Library()


@register.simple_tag
def inquiry(form_data):
    return form_data['qq']
