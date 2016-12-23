from django.core.exceptions import ValidationError
from pyparsing import ParseBaseException
from django.core.validators import MaxLengthValidator


class ParamValidator(object):
    def __init__(self, file_support=False):
        self._file_support = file_support
        
    def __call__(self, value):

        # Imported here to avoid circular dependency
        from .parser import parse_fields
        try:
            par = parse_fields(value, self._file_support)
        except ParseBaseException as err:
            # Parser Error
            raise ValidationError(str(err))
        except ValueError as err:
            # Error while creating Param
            raise ValidationError(str(err))



class ParamLengthValidator(MaxLengthValidator):
    
    def clean(self, x):
        return len(str(x))



class ParamFormFieldValidator(object):

    def __init__(self, param):
        self._param = param

    def __call__(self, value):
        try:
            self._param.validate(value)
        except ValueError as err:
            raise ValidationError(err)
        except TypeError as err:
            raise ValidationError(err)
