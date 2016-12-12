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
    raise NotImplementedError


def StdFieldFactory(param, name):
    """Form field  factory for fields using standard fields, that is:
    Bool, Text, TextArea, Integer, Decimal, Dimmension"""
    field_args = {
        'help_text': param.help_text or None,
        'label': param.label or expand_name(name),
        'initial': param.default,
        'required': param.default is None,
        'validators': [ParamFormFieldValidator(param),]}

    # Change widget for hidden fields
    if param.hidden or False:
        field_args['widget'] = forms.HiddenInput()

    # Generate correct Field type or ChoiceField
    choices = param.get_choices()
    if choices:
        field_args['coerce'] = param.native_type
        field_args['choices'] = choices
        field_args.pop('validators', None)
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
        - params: ParamDict

    Examples: 
        https://jacobian.org/writing/dynamic-form-generation/
        http://stackoverflow.com/questions/5871730/need-a-minimal-django-file-upload-example
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self._params = kwargs.pop('params')
        super(ParamInputForm, self).__init__(*args, **kwargs)
       
        # Add all visible fields from ParamDict to the form
        for name, param in self._params.items():
            self.fields[name] = ParamFieldFactory(param, name)

    def clean(self):
        # When a form's non-string and non-required field is not supplied by
        # the user, None is asigned by default. Here all those fields are 
        # removed after validation so the default value for the parameter
        # is used by PartGenerator.
        cd = dict((k, v) for k, v in self.cleaned_data.items() if v is not None) 
        return self.cleaned_data
        self.cleaned_data = cd
        return self.cleaned_data


