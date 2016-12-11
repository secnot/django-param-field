from django import forms
from .validators import *
from .params import *


class ForeignKeyField(forms.ModelChoiceField):
    pass

class ForeignKeyChoiceField(forms.ChoiceField):
    pass

class GeneratorField(forms.CharField):   
    def to_python(self, value):
        """Convert part generator slug"""
        from .models import PartGenerator
        try:
            obj = PartGenerator.objects.get(slug=value)
            return obj
        except (ValueError, TypeError, ObjectDoesNotExist):
            raise forms.ValidationError(
                _("Unknown generator %(value)s"),
                params={'value': value})




FORM_FIELD_CLASS = {
    BoolParam: forms.BooleanField,
    TextParam: forms.CharField,
    TextAreaParam: forms.CharField,
    IntegerParam: forms.IntegerField,
    DecimalParam: forms.DecimalField,
    DimmensionParam: forms.DecimalField,
    GeneratorParam: ForeignKeyField,
    FileParam: ForeignKeyField,
    ImageParam: ForeignKeyField,
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



def ForeignKeyFieldFactory(param, name):
    """Form field factory for all params using one"""
    choices = param.get_choices()
    if choices:
        # Construct a query that returns the models present in choices.
        choices = [getattr(c, param.model_field) for c in choices]
        query_args = {param.model_field+'__in': choices_field}
        query = param.model_class.objects.filter(query_args)
    else:
        query = param.model_class.objects.all()

    field_args = {
        'help_text': param.help_text or None,
        'label': param.label or expand_name(name),
        'initial': param.default,
        'required': param.default is None,
        'queryset': query}

    return forms.ModelChoiceField(**field_args)


def StdFieldFactory(param, name):
    """Form field  factory for fields using standard fields, that is:
    Bool, Text, TextArea, Integer, Decimal, Dimmension"""
    field_args = {
        'help_text': param.help_text or None,
        'label': param.label or expand_name(name),
        'initial': param.default,
        'required': param.default is None,
        'validators': [ParamFormFieldValidator(param),]}

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
    if field_class == ForeignKeyField:
        return ForeignKeyFieldFactory(param, name)
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
        Argument:
            part_gen (PartGenerator): Form's part generator instance

        """
        self._params = kwargs.pop('params')
        super(ParamInputForm, self).__init__(*args, **kwargs)
       
        # Add all visible fields from ParamDict to the form
        for name, param in self._params.items():
            if not param.visible or not isinstance(param, Param):
                continue
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


