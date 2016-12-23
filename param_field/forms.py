from django import forms
from .validators import *
from .params import *


FORM_FIELD_CLASS = {
    BoolParam: forms.BooleanField,
    TextParam: forms.CharField,
    TextAreaParam: forms.CharField,
    IntegerParam: forms.IntegerField,
    DecimalParam: forms.DecimalField,
    DimmensionParam: forms.DecimalField,
    FileParam: forms.FileField,
    ImageParam: forms.ImageField,
}


# Field cutom widget
FORM_FIELD_WIDGET = {
    BoolParam: None,
    TextParam: None,
    TextAreaParam: forms.Textarea,
    IntegerParam: None,
    DecimalParam: None,
    DimmensionParam: None,
    FileParam: None,
    ImageParam: None,
}


def expand_name(name):
    """Convert param  name string from 'this_is_a_name' to 'This is a name' so
    it can be used as the a field label
    
    Arguments:
        -name (string):
    Returns:
        string
    """
    chars = '*+-_=,;.:\\/[]{}()<>#@$%&'
    text = name.lower()
    for c in chars:
        text = text.replace(c, ' ')
    text = text[0].upper() + text[1:]
    return text



def FileFieldFactory(param, name):
    """Form field factory for all File fields"""    
    field_args = {
        'help_text': param.help_text or None,
        'label': param.label or expand_name(name),
        'required': param.required,}

    return FORM_FIELD_CLASS[type(param)](**field_args)


def StdFieldFactory(param, name):
    """Form field  factory for fields using standard fields, that is:
    Bool, Text, TextArea, Integer, Decimal, Dimmension"""
    field_args = {
        'help_text': param.help_text or None,
        'label': param.label or expand_name(name),
        'initial': param.default,
        'required': param.required,
        'validators': [ParamFormFieldValidator(param),]} # Use param validator
   
    # Add max/min value limits to form field instead of using only param 
    # field validation. This way the browser limits user input instead of
    # returning an error when the form is posted and the numbers are out 
    # of range.
    if getattr(param, 'max', None) is not None:
        field_args['max_value'] = param.max

    if getattr(param, 'min', None) is not None:
        field_args['min_value'] = param.min

    # Add custom widget if any
    field_args['widget'] = FORM_FIELD_WIDGET[type(param)]
    
    # Change widget for hidden fields
    if getattr(param, 'hidden', None):
        field_args['widget'] = forms.HiddenInput()
    
    choices = param.get_choices()
 
    # Generate correct Field type or ChoiceField
    if choices:
        field_args['coerce'] = param.native_type
        field_args['choices'] = choices
        
        # Remove options not supported by Typed choice field
        field_args.pop('validators', None)
        field_args.pop('min_value', None)
        field_args.pop('max_value', None)
        return forms.TypedChoiceField(**field_args)
    else:
        return FORM_FIELD_CLASS[type(param)](**field_args)


def ParamFieldFactory(param, name):
    field_class = FORM_FIELD_CLASS[type(param)]
    if field_class in (forms.FileField, forms.ImageField):
        return FileFieldFactory(param, name)
    else:
        return StdFieldFactory(param, name)


class ParamInputForm(forms.Form):
    """
    Form with fields for the parametes of a PartGenerator, can
    be used to validate inputs
   
    Arguments:
        - params (ParamDict): Containing form fields
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self._params = kwargs.pop('params')
        super(ParamInputForm, self).__init__(*args, **kwargs)
       
        # Add all fields from ParamDict to the form
        for name, param in self._params.items():
            self.fields[name] = ParamFieldFactory(param, name)
