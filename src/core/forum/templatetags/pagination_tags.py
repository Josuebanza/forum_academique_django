# forum/templatetags/pagination_tags.py
from django import template
from urllib.parse import urlencode

#register = template.Library()
# @register.simple_tag(takes_context=True)
# def url_replace_param(context, field, value):
#     """
#     Replaces a GET parameter with a new value in the current URL query string.
#     Usage: {% url_replace_param 'page' page_obj.next_page_number %}
#     """
#     dict_ = context['request'].GET.copy()
#     dict_[field] = value
#     return dict_.urlencode()

# @register.simple_tag(takes_context=True)
# def url_remove_param(context, param):
#     """
#     Removes a GET parameter from the current URL query string.
#     Usage: {% url_remove_param 'query' %}
#     """
#     dict_ = context['request'].GET.copy()
#     if param in dict_:
#         del dict_[param]
#     return dict_.urlencode()


register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace_param(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.simple_tag(takes_context=True)
def url_remove_param(context, param):
    dict_ = context['request'].GET.copy()
    if param in dict_:
        del dict_[param]
    return dict_.urlencode()