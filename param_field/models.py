from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from pyparsing import ParseBaseException
from .params import ParamDict
from .validators import ParamValidator


MAX_PARAM_FIELD_LENGTH = 3000

# Create your models here.

class ParamField(models.TextField):

    description = _('Parameter field')

    def __init__(self, *args, **kwargs):
        """
        Arguments:
            file_support(bool): Enable or disable support for file fields.
        """
        kwargs['max_length'] = MAX_PARAM_FIELD_LENGTH
        kwargs['blank'] = True
        
        self._file_support = kwargs.pop('file_support', True)
    
        super(ParamField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        del kwargs['blank']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        try:
            return ParamDict(value, self._file_support)
        except ParseBaseException as err:
            raise ValidationError(str(err))
        except ValueError as err:
            raise ValidationError(str(err))

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
        defaults = {'validators': [ParamValidator(),]}
        defaults.update(kwargs)
        return super(ParamField, self).formfield(**defaults)

