from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django import forms
from pyparsing import ParseBaseException
from .params import ParamDict
from .validators import ParamValidator, ParamLengthValidator
from .conf import settings


# Create your models here.

class ParamField(models.TextField):

    description = _('Parameter field')

    def __init__(self, *args, **kwargs):
        """
        Arguments:
            file_support(bool): Enable or disable support for file fields.
                default is True
        """
       
        if kwargs.get('max_length', None) is None:
            kwargs['max_length'] = settings.PARAM_FIELD_MAX_LENGTH

        kwargs['blank'] = True
        
        self._file_support = kwargs.pop('file_support', True)
        super(ParamField, self).__init__(*args, **kwargs)
        self.validators.append(ParamLengthValidator(self.max_length))

    def deconstruct(self):
        """Cleanup of added kwargs"""
        name, path, args, kwargs = super().deconstruct()

        if self.max_length == settings.PARAM_FIELD_MAX_LENGTH:
            del kwargs['max_length']

        del kwargs['blank']

        if not self._file_support:
            kwargs['file_support'] = False

        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        try:
            return ParamDict(value, self._file_support)
        except ParseBaseException as err:
            # Couldn't parse form definition return empty dict
            return ParamDict(value, self._file_support, parse=False)
        except ValueError as err:
            # Couldn't parse form definition return empty dict
            return ParamDict(value, self._file_support, parse=False)

    def get_prep_value(self, value):
        """Convert objects to string"""
        return str(value)

    def to_python(self, value):
        if isinstance(value, ParamDict):
            return value

        if value is None:
            return Value

        try:
            return ParamDict(value, self._file_support)
        except ParseBaseException as err:
            raise ValidationError(str(err))
        except ValueError as err:
            raise ValidationError(str(err))

    def formfield(self, **kwargs):
        """So validation can be added"""
        defaults = {
                'validators': [ParamValidator(self._file_support)], 
                'widget': forms.Textarea,
                'max_length': self.max_length}
        defaults.update(kwargs)
        return super(ParamField, self).formfield(**defaults)

