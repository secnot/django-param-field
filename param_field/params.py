from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from numbers import Number
from collections import OrderedDict
import json
from .conf import settings


class ParamDict(OrderedDict):
  
    def __init__(self, fields='', file_support=False, parse=True):
        """
        Arguments:
            fields (str): String containig fields definitions.
            file_support(book): 
            parse(bool): If True parse field string, else just store
                original string and return empy ParamDict
        """
        from .parser import parse_fields # Solve circular import
        super(ParamDict, self).__init__()

        # Store source used to generate ParamDict
        self._source = fields

        if parse:
            f = parse_fields(fields or '', file_support)
        else:
            f = {}

        for name, field in f.items():
            self[name] = field
    
    def form(self, *args, **kwargs):
        """Return a form containig all parameters stored in ParamDict
        Arguments:
            *args and **kwargs: Are the arguments you would normally 
            pass to a form
        """
        # Imported here to avoid circular dependency
        from .forms import ParamInputForm
        
        # If there are no defined fields returns Nones instead of
        # an empty form.
        if len(self) == 0:
            return None

        kwargs['params'] = self
        return ParamInputForm(*args, **kwargs)

    def validate(self, request):
        """
        Validate request against ParamDict parameters

        A request is valid if there is a valid value for each required parameter 
        or in it absence if the parameter has a default value.

        Arguments:
            request (dict): Dictionary containing (param_name: value)
        """
        # Check no unknown parameter present in the request
        for name, value in request.items():
            if self.get(name, None) is None:
                raise ValidationError("Unknown parameter '{}'".format(name))

        # Validate request against parameter definitions
        for name, value in self.items():
            # Check a valid value was provided for each required parameter
            # without a default value.
            try:
                value = request.get(name, None)
                param = self[name]
                if param.required and value is None:
                    if param.get_default() is None:
                        raise ValidationError("No value supplied for {}"\
                                .format(name))
                else:
                    self[name].validate(value)
            except (TypeError, ValueError, ValidationError) as err:
                raise ValidationError(str(err))

    def add_defaults(self, request):
        """
        Add default values to missing parameters when available.

        Arguments:
            request (dict): dict containing parameter values

        Returns:
            dict: new dictionary with default values
        """
        with_defaults = dict(request)

        for name, param in self.items():
            default = param.get_default()
            if default is not None and request.get(name, None) is None:
                with_defaults[name] = default

        return with_defaults

        dict_str = ""
        for name, param in self.items():        
            dict_str += name+':'+str(param)+'\n'

        return dict_str

    def __str__(self):
        if self._source:
            return self._source
        else:
            # Generate from fields
            return '\n'.join(["{}:{}"\
                .format(name, str(param)) for name, param in self.items()])


# Property -> allowed types | limits

class Param(object):
    native_type = str
   
    # Property and type supported, in order of initialization
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('choices', list, None),
        ('default', str, '')] 
    
    def _init_choices(self, value):
        """Initialize Param for choices property"""
        choices =[]
        for elem in value:
            try:
                ep = self.deserialize_value(elem)
                self.validate(ep)
                choices.append(ep)
            except (TypeError, ValueError, ValidationError):
                raise ValueError("Invalid 'choices' value '{}'".format(elem))

        self.choices = choices
    
    def _init_default(self, value):
        """Initialize Param for default property"""
        try:
            self.default = self.deserialize_value(value)
            self.validate(self.default)
        except (TypeError, ValueError, ValidationError):
            raise ValueError("Invalid 'default' value '{}'".format(value))

    def _init_label(self, value):
        """Initialize Param for label property"""
        if len(value)>settings.PARAM_LABEL_MAX_LENGTH:
            raise ValueError("'{}' label too long".format(value))
        self.label = value

    def _init_hidden(self, value):
        """Verify default value is provided when field hidden"""
        self.hidden = value
      
        # No choices are needed when the user can't seet the field
        if self.hidden and hasattr(self, 'choices'):
            self.choices = None

        # Default value required for hidden fields
        if self.hidden and (not hasattr(self, 'default') or self.default is None):
            raise ValueError('A default value must be provided for hidden parameters')

    def _init_help_text(self, value):
        if len(value)>settings.PARAM_HELP_TEXT_MAX_LENGTH:
            raise ValueError("help text too long".format(value))
        self.help_text = value

    def __init_property(self, name, value): 
        """
        Initialize property by calling its custom initialzation function or
        storing its value if none is available.
        """
        allowed_type = self._prop_type_dict[name]
        if not isinstance(value, allowed_type):
            allowed_type.__class__.__name__
            err = "'{}' expected '{}' received '{}'"\
                .format(name, allowed_type.__name__, value.__class__.__name__)
            raise ValueError(err)

        init_func = getattr(self, '_init_'+name, None)
        if init_func:
            init_func(value)
        else:
            setattr(self, name, value)
    
    def __init__(self, *args, **kwargs):
        """Custom init method responsible of initializing and checking parameters"""
        # Initialize all possible properties to default values
        self._prop_type_dict = {}
        for prop, typ, default in self.allowed_properties:
            self._prop_type_dict[prop] = typ
            setattr(self, prop, default)

        # Check only allowed properties were provided
        for prop, value in kwargs.items():
            if prop not in self._prop_type_dict:
                raise ValueError("Unexpected property '{}'".format(prop))

        # If available call custom initialization function for each property 
        # (in the order specified by allowed_properties)
        for name, typ, default in self.allowed_properties:
            if name in kwargs:
                self.__init_property(name, kwargs[name]) 

    def _validate_choices(self, value):
        if self.choices and not value in self.choices:
            raise ValidationError("Not a valid choice")

    def get_choices(self):
        """Generate a (choice, choice_str) tuple list used by form fields.
        
        Returns:
            List
            None
        """
        if hasattr(self, 'choices') and self.choices is not None:
            return [(c, str(c)) for c in self.choices]
        else:
            return None

    def get_default(self):
        if hasattr(self, 'default'):
            return self.default
        else:
            return None

    def validate(self, value):
        """Check value against parameter limits"""
        if not type(value) == self.native_type:
            err = "Expected '{}' received '{}'"\
                .format(self.native_type.__name__, type(value).__name__)
            raise TypeError(err)
        
        # Validate against available property validators
        for name, typ, default in self.allowed_properties:
            validate_func = getattr(self, '_validate_'+name, None)
            if validate_func:
                validate_func(value) 

    def is_valid(self, value):
        try:
            self.validate(value)
            return True
        except (ValueError, TypeError, ValidationError): 
            return False

    def deserialize_value(self, value):
        """Convert from value representation to the actual value object"""
        if not type(value) == self.native_type:
            err = "Expected '{}' received '{}'"\
                .format(self.native_type.__name__, type(value).__name__)
            raise TypeError(err)
        return value

    def serialize_value(self, value):
        """to_python reverse step"""
        return value

    def value_to_str(self, value):
        """Convert property value to the representation used in the
        parameter definition language, so it can be parsed. This is
        later reverser by to python"""
        value = self.serialize_value(value)
        if type(value) == list:
            return '['+', '.join([self.value_to_str(v) for v in value])+']'
        elif type(value) == str:
            return json.dumps(value)
        else:
            return str(value)

    def to_str(self):
        """Convert parameter to its parameter definition language
        representation, including all properties with user defined
        values."""

        # Render properties
        prop_str = ""
        for name, typ, default in self.allowed_properties:
            
            try:
                value = getattr(self, name)
            except AttributeError:
                continue

            if value == default:
                continue
            
            if type(value)!=typ:
                err="'{}' type should be {} not {}"\
                    .format(name, str(typ), str(type(value)))
                raise ValueError(err)

            prop_str += ' {}:{}'.format(name, self.value_to_str(value))

        return self.type_name+('->'+prop_str if prop_str else '')

    def __str__(self):
         return self.to_str()


class NumberMixin(object):

    def _init_min(self, value):
        if not self.is_valid(self.native_type(value)):
            raise ValueError("Invalid 'min' value")
        if value > self.max:
            raise ValueError("Invalid 'min' value, must be less or equal to 'max'")

        self.min = value

    def _init_max(self, value):
        if not self.is_valid(self.native_type(value)):
            raise ValueError("Invalid 'max' value")
        if value < self.min:
            raise ValueError("Invalid 'max' value, must be greater or equal to 'min'")

        self.max = value

    def _validate_min(self, value):
        if self.min is not None and value < self.min:
            err = "Value must be greater than or equal to {}"\
                    .format(self.min)
            raise ValidationError(err)

    def _validate_max(self, value):
        if self.max is not None and value > self.max:
            err = "Value must be smaller than or equal to {}"\
                    .format(self.max)
            raise ValidationError(err)

    def _validate_even(self, value):
        if self.even and value%2==1:
            raise ValidationError("Value must be even")

    def _validate_odd(self, value):
        if self.odd and value%2==0:
             raise ValidationError("Value must be odd")


class StringMixin(object):

    def _init_max_length(self, value):
        if value > settings.PARAM_TEXT_MAX_LENGTH or value < 0:
            raise ValueError("Invalid 'max_length' value")
        if value < self.min_length:
            raise ValueError("Invalid 'max_length' value, must be greater or equal to 'min_length'")

        self.max_length = value
    
    def _init_min_length(self, value):
        if value > settings.PARAM_TEXT_MAX_LENGTH or value < 0:
            raise ValueError("Invalid 'min_length' value")
        if value > self.max_length:
            raise ValueError("Invalid 'min_length' value, must be less or equal to 'max_length'")

        self.min_length = value
    
    def _validate_max_length(self, value):
        if self.max_length is not None and len(value)>self.max_length:
            err = "Can be at most {} characters long".format(self.max_length)
            raise ValidationError(err)
    
    def _validate_min_length(self, value):
        if self.min_length is not None and len(value)<self.min_length:
            err = "Has to be at least {} characters long".format(self.min_length)
            raise ValidationError(err)



class BoolParam(Param):
    native_type = bool
    type_name = 'Bool'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('default', bool, None),
        ('hidden', bool, False)]

class IntegerParam(Param, NumberMixin):
    native_type = int
    type_name = 'Integer'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('even', bool, False),
        ('odd', bool, False),
        ('min', int, settings.PARAM_INT_MIN),
        ('max', int, settings.PARAM_INT_MAX),
        ('choices', list, None),
        ('default', int, None),
        ('hidden', bool, False)]

class DecimalParam(Param, NumberMixin):
    native_type = Decimal
    type_name = 'Decimal'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('max_digits', int, settings.PARAM_DECIMAL_MAX_DIGITS),
        ('max_decimals', int, settings.PARAM_DECIMAL_MAX_DECIMALS),
        ('min', Decimal, settings.PARAM_DECIMAL_MIN),
        ('max', Decimal, settings.PARAM_DECIMAL_MAX),
        ('choices', list, None),
        ('default', Decimal, None),
        ('hidden', bool, False)]

    abs_max_digits = settings.PARAM_DECIMAL_MAX_DIGITS
    abs_max_decimals = settings.PARAM_DECIMAL_MAX_DECIMALS

    @staticmethod
    def _decimal_digits(dec):
        """Return decimal number digits"""
        return len(dec.as_tuple().digits)

    @staticmethod
    def _decimal_decimals(dec):
        """Return decimal number decimals"""
        return abs(dec.as_tuple().exponent)

    def _init_max_digits(self, value):
        if value <= 0:
            raise ValueError("Invalid 'max_digits' value, must be greater than zero")

        if value > self.abs_max_digits:
            raise ValueError("Invalid 'max_digits' value,  too big (max: {})".format(
                self.abs_max_digits))
        self.max_digits = value
    
    def _init_max_decimals(self, value):
        if value < 0:
            raise ValueError("Invalid 'max_decimals' value, must be greater or equal to zero")

        if value > self.abs_max_decimals:
            raise ValueError("Invalid 'max_decimals' value, too big (max: {})".format(
                    self.abs_max_decimals))

        if value >self.max_digits:
            raise ValueError("Invalid 'max_decimas' must be smaller or equal to 'max_digits'")

        self.max_decimals = value

    def _validate_max_digits(self, value):   
        if DecimalParam._decimal_digits(value) > self.max_digits:
            raise ValueError("Too many digits. (max: {})".format(self.max_digits))

    def _validate_max_decimals(self, value):
        if DecimalParam._decimal_decimals(value) > self.max_decimals:
            raise ValueError("Too many decimals. (max: {})".format(self.max_decimals))

class DimmensionParam(DecimalParam):
    native_type = Decimal
    type_name = 'Dimmension' 
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('max_digits', int, settings.PARAM_DIMMENSION_MAX_DIGITS),
        ('max_decimals', int, settings.PARAM_DIMMENSION_MAX_DECIMALS),
        ('min', Decimal, max(Decimal("0"), settings.PARAM_DIMMENSION_MIN)),
        ('max', Decimal, settings.PARAM_DIMMENSION_MAX),
        ('choices', list, None),
        ('default', Decimal, None),
        ('hidden', bool, False)]
    
    abs_max_digits = settings.PARAM_DIMMENSION_MAX_DIGITS
    abs_max_decimals = settings.PARAM_DIMMENSION_MAX_DECIMALS

class TextParam(Param, StringMixin):
    native_type = str
    type_name = 'Text'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('min_length', int, 0),
        ('max_length', int, settings.PARAM_TEXT_MAX_LENGTH),
        ('choices', list, None),
        ('default', str, None),
        ('hidden', bool, False)]

class TextAreaParam(TextParam):
    type_name = 'TextArea'


# File Params
class FileParam(Param, StringMixin):
    native_type = str
    type_name = 'File'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True)]

class ImageParam(FileParam):
    native_type = str
    type_name = 'Image'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True)]


