from django.utils.numberformat import format
from django import template

register = template.Library()


@register.filter
def numberformat_br(number, decimal_pos=2):
    return format(number, decimal_sep=',', decimal_pos=decimal_pos, grouping=3, thousand_sep='.', force_grouping=3)


@register.filter
def number_br_int(number):
    number = int(number)
    return format(number, decimal_sep='', decimal_pos=0, grouping=3, thousand_sep='.', force_grouping=3)


@register.filter
def monetary_br(number):
    number = float(number)
    return format(number, decimal_sep=',', decimal_pos=2, grouping=3, thousand_sep='.', force_grouping=3)
