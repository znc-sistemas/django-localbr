# -*- coding: utf-8 -*-
import datetime

from django.forms.widgets import Widget, TextInput, MultiWidget, Select, DateInput
from django.utils.safestring import mark_safe

# Python 2.3 fallbacks
try:
    from decimal import Decimal
except ImportError:
    from django.utils._decimal import Decimal


class BRJsDateWidget(DateInput):
    """
    Renders a text for input and a jscalendar to select dates
    """
    def render(self, name, value, attrs=None):
        output = []
        textinput = TextInput(attrs={"class": "dateselector"})
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):

            value = value.strftime("%d/%m/%Y")
        output.append(textinput.render(name, value, attrs))
        return mark_safe(''.join(output))

    class Media:
        css = {
           'all': ('css/south-street/jquery-ui-1.7.2.custom.css',)
        }

        js = ('js/jquery-ui-1.7.2.custom.min.js', 'js/ui.datepicker-pt-BR.js', 'js/init_datepicker.js',)


class BRDecimalWidget(TextInput):

    def render(self, name, value, attrs=None):
        if isinstance(value, Decimal):
            value = str(value).replace('.', ',')
        return super(BRDecimalWidget, self).render(name, value, attrs)


class BRFloatWidget(TextInput):

    def render(self, name, value, attrs=None):
        if isinstance(value, float):
            value = "%.2f" % value
            value = value.replace('.', ',')
        return super(BRFloatWidget, self).render(name, value, attrs)


class PointWidget(MultiWidget):
    """
    A widget that renders text inputs for X and Y coordinates of a point
    """
    def __init__(self, attrs=None, srs=None):
        self.srs = srs
        widgets = (BRFloatWidget(attrs=attrs), BRFloatWidget(attrs=attrs))
        super(PointWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if self.srs is not None:
                value.transform(self.srs)
            return [value.x, value.y]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u"X: %s &nbsp; Y: %s" % (rendered_widgets[0], rendered_widgets[1])
