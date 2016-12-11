from django.core.exceptions import ValidationError
from pyparsing import ParseBaseException


class ParamValidator(object):
    def __init__(self, fk_support=False):
        self._fk_support = fk_support
        self._fk_support = False
        
    def __call__(self, value):

        # Imported here to avoid circular dependency
        from .parser import parse_fields
        try:
            par = parse_fields(value, self._fk_support)
        except ParseBaseException as err:
            # Parser Error
            raise ValidationError(str(err))
        except ValueError as err:
            # Error while creating Param
            raise ValidationError(str(err))


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
