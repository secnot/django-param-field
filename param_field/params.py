from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from numbers import Number
from collections import OrderedDict
import json
from .limits import *

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

        self._original_source = fields

        if parse:
            f = parse_fields(fields or '', file_support)
        else:
            f = {}

        for name, field in f.items():
            self[name] = field

    def __str__(self):
        if self._original_source:
            return self._original_source
        else:
            # Generate from fields
            return '\n'.join(["{}:{}"\
                .format(name, str(param)) for name, param in self.items()])

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

    def serialize(self, request):
        """Convert each value to its representation so it can be easily stored

        Argumens:
            request (dictionary): value for each parameter.
        """
        serialized = {}
        for name, value in request.items():
            serialized[name] = self[name].serialize_value(value)
        return serialized

    def deserialize(self, request):
        """The oposite step to 'request_to_dict' convert all values from its 
        representation to its real python value, that can be later be validated.
        
        Arguments:
            request (dict): Request dict containing serialized values
        """
        deserialized = {}
        for name, value in request.items():
            deserialized[name] = self[name].deserialize_value(value)
        return deserialized

    def validate(self, request):
        """
        Validate request against ParamDict parameters.

        Arguments:
            request (dict):
        """
        # Check no unknown parameter present in the request
        for name, value in request.items():
            if self.get(name, None) is None:
                raise ValidationError("Parameter '{}' does not exists"\
                        .format(name))

        # Validate request against parameter definitions
        for name, value in self.items():
            # TODO if no value was provided if there is a default value the 
            # request is valid
            try:
                value = request.get(name, None)
                param = self[name]
                if value is None:
                    default = param.get_default()
                    if default is None:
                        raise ValidationError("No value supplied for {}"\
                                .format(name))
                else:
                    self[name].validate(value)
            except (TypeError, ValueError, ValidationError) as err:
                raise ValidationError(str(err))

    def add_defaults(self, request):
        """
        Add missing parameters using default values.

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

    def param_count(self):
        """Returns number of parameters in the dictionary, constants
        are not counted.
        
        Returns:
            int
        """
        params = 0
        for name, value in self.items():
            if isinstance(value, Param):
                params += 1
        return params

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
        if len(value)>LABEL_MAX_LENGTH:
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
        if len(value)>HELP_TEXT_MAX_LENGTH:
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
        """Convert from value representation to the actual value object
        for example: slug string TO model instance
        USED BY FOREIGN KEY AND FILE PARAMS  
        """
        if not type(value) == self.native_type:
            err = "Expected '{}' received '{}'"\
                .format(self.native_type.__name__, type(value).__name__)
            raise TypeError(err)
        return value

    def serialize_value(self, value):
        """to_python reverse step
        USED BY FOREIGN KEY AND FILE PARAMS 
        """
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
        self.min = value

    def _init_max(self, value):
        if not self.is_valid(self.native_type(value)):
            raise ValueError("Invalid 'max' value")
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
        if value > STRING_MAX_LENGTH or value < 0:
            raise ValueError("Invalid 'max_length' value")
        self.max_length = value
    
    def _init_min_length(self, value):
        if value > STRING_MAX_LENGTH or value < 0:
            raise ValueError("Invalid 'min_length' value")
        self.min_length = value
    
    def _validate_max_length(self, value):
        if self.max_length is not None and len(value)>self.max_length:
            err = "Must be at most {} characters long".format(self.max_length)
            raise ValidationError(err)
    
    def _validate_min_length(self, value):
        if self.min_length is not None and len(value)<self.min_length:
            err = "Must be at least {} characters long".format(self.min_length)
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
        ('min', int, INT_MIN),
        ('max', int, INT_MAX),
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
        ('min', Decimal, REAL_MIN),
        ('max', Decimal, REAL_MAX),
        ('choices', list, None),
        ('default', Decimal, None),
        ('hidden', bool, False)]

class DimmensionParam(Param, NumberMixin):
    native_type = Decimal
    type_name = 'Dimmension'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('min', Decimal, Decimal('0.0')),
        ('max', Decimal, REAL_MAX),
        ('choices', list, None),
        ('default', Decimal, None),
        ('hidden', bool, False)]

class TextParam(Param, StringMixin):
    native_type = str
    type_name = 'Text'
    allowed_properties = [
        ('label', str, ''),
        ('help_text', str, ''),
        ('required', bool, True),
        ('min_length', int, 0),
        ('max_length', int, STRING_MAX_LENGTH),
        ('choices', list, None),
        ('default', str, None),
        ('hidden', bool, False)]

class TextAreaParam(TextParam):
    type_name = 'TextArea'
    pass
    #TODO: Custom widget


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


