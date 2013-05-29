# -*- coding: utf-8 -*-

from django.forms import FloatField, DecimalField, MultiValueField, ValidationError
from django.utils.encoding import smart_unicode
from widgets import BRDecimalWidget, PointWidget, BRFloatWidget
from django.forms.fields import EMPTY_VALUES
from django.utils.safestring import mark_safe
from django.forms.fields import Field
from django.contrib.gis.geos import Point
from django.contrib.localflavor.br import forms as lfbr_forms

import re


class BRPhoneNumberField(Field):

    def clean(self, value):
        super(BRPhoneNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = re.sub('(\(|\)|\s+)', '', smart_unicode(value))
        m = re.compile(
            r'^(\d{2})[-\.]?((\d{5})|(\d{4}))[-\.]?(\d{4})$').search(value)
        if m:
            gs = m.groups()
            return u'%s-%s-%s' % (gs[0], gs[1], gs[4])
        raise ValidationError(u'Formato Errado')


class BRDecimalField(DecimalField):
    widget = BRDecimalWidget

    def clean(self, value):
        value = str(value).replace('.', '').replace(',', '.')
        return super(BRDecimalField, self).clean(value)


class BRFloatField(FloatField):
    widget = BRFloatWidget

    def clean(self, value):
        value = value.replace('.', '').replace(',', '.')
        return super(BRFloatField, self).clean(value)


def validate_coord_br_extent(coord_type, x=None, y=None, south=True):
    if coord_type == 'geo':
        if x is not None:
            if x < -75.0 or x > -30.0:
                return {'result': False, 'msg': u"A coordenada X está fora da área do Brasil<br />(maior que -75 e menor que -30)"}
        if y is not None:
            if y < -35.0 or y > 5.0:
                return {'result': False, 'msg': u"A coordenada Y está fora da área do Brasil<br />(maior que -35 e menor que +5)"}
    elif coord_type == 'utm':
        if x is not None:
            if x < 100000.00 or x > 900000.0:
                return {'result': False, 'msg': u"A coordenada X está fora da faixa<br />(maior que 100000 e menor que 900000)"}
        if y is not None:
            if y < 0 or (south and (y < 6000000 or y > 10000000)) or (not south and (y > 1000000)):
                return {'result': False, 'msg': u"A coordenada Y está fora da área do Brasil<br />(%s)" % (south and 'maior que 6000000 e menor que 10000000' or 'maior que 0 e menor que 1000000')}
    else:
        return {'result': False, 'msg': u'Tipo de coordenada não informado!'}
    if x is None and y is None:
        return {'result': False, 'msg': u'Nenhuma coordenada informada!'}

    return {'result': True, "msg": u""}


class PointField(MultiValueField):

    """
    A form field that handles django.contrib.gis.models.PointField data
    """
    widget = PointWidget
    default_error_messages = {
        'invalid_coordinate': (u'Coordenada inválida'),
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        if 'dest_srid' in kwargs:
            self.dest_srid = kwargs['dest_srid']
            del kwargs['dest_srid']
        else:
            self.dest_srid = None
        if 'srid' in kwargs:
            self.srid = kwargs['srid']
            del kwargs['srid']
        else:
            self.srid = None

        fields = (
            BRFloatField(),
            BRFloatField(),
        )
        super(PointField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if (data_list[0] and data_list[1] in EMPTY_VALUES) or (data_list[0] in EMPTY_VALUES and data_list[1]):
                raise ValidationError(self.error_messages['invalid_coordinate'])
            x, y = data_list[0], data_list[1]
            geom = Point(x, y, srid=self.srid)

            if self.srid is not None:
                coord_type = self.srid == 4618 and 'geo' or 'utm'
                south = (self.srid >= 29190 and self.srid <= 29194)
                val = validate_coord_br_extent(coord_type,
                    x=geom.x, y=geom.y, south=south)
                if not val['result']:
                    raise ValidationError(mark_safe(val['msg']))

            if self.dest_srid is not None:
                geom.transform(self.dest_srid)
            return geom
        return None


class BRCPFField(lfbr_forms.BRCPFField):

    def __init__(self, always_return_formated=False, return_format=u'%s.%s.%s-%s', *args, **kwargs):
        self.always_return_formated, self.return_format = always_return_formated, return_format
        super(BRCPFField, self).__init__(*args, **kwargs)
        self.help_text = u'ex. 000.000.000-00'

    def clean(self, value):
        value = super(BRCPFField, self).clean(value)

        # exclui CPF somente com digitos 0 ou 9
        if value in ('0' * 11, '9' * 11):
            raise ValidationError(self.error_messages['invalid'])

        if value not in EMPTY_VALUES:
            if self.always_return_formated:
                return self.return_format % tuple(re.findall(r'(\d{2,3})', re.sub('[-\.]', '', value)))
        return value


class BRCNPJField(lfbr_forms.BRCNPJField):

    def __init__(self, always_return_formated=False, return_format=u'%s.%s.%s/%s-%s', *args, **kwargs):
        self.always_return_formated, self.return_format = always_return_formated, return_format
        super(BRCNPJField, self).__init__(*args, **kwargs)
        self.help_text = u'ex. 000.000.000-00'

    def clean(self, value):
        value = super(BRCNPJField, self).clean(value)
        self.help_text = u'00.000.000/0000-00'

        if value not in EMPTY_VALUES:
            if self.always_return_formated:
                m = re.match(r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})',
                    re.sub('[-/\.]', '', value))
                return self.return_format % tuple(m.groups())
        return value
