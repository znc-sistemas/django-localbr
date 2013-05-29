from django.utils.numberformat import format
from django import template

register = template.Library()


@register.filter
def numberformat_br(number):
    return format(number, decimal_sep=',', decimal_pos=2, grouping=3, thousand_sep='.', force_grouping=3)
