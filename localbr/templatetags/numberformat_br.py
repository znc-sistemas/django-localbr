from localbr.utils import numberformat
from django import template

register = template.Library()


@register.filter
def numberformat_br(number, decimal_pos=2):
    if number in (None, ''):
        return ''
    return numberformat(number, decimal_sep=',', decimal_pos=decimal_pos, grouping=3, thousand_sep='.', force_grouping=3)


@register.filter
def number_br_int(number):
    if number in (None, ''):
        return ''
    number = int(number)
    return numberformat(number, decimal_sep='', decimal_pos=0, grouping=3, thousand_sep='.', force_grouping=3)


@register.filter
def monetary_br(number):
    if number in (None, ''):
        return ''
    number = float(number)
    return numberformat(number, decimal_sep=',', decimal_pos=2, grouping=3, thousand_sep='.', force_grouping=3)
