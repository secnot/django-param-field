from django.test import TestCase
from django.core.exceptions import ValidationError
from param_field.models import ParamField
from param_field.params import *
from param_field.forms import *



class TestParamField(TestCase):

    def test_parse(self):
        """Test strings are parsed into a ParamDict"""
        pf = ParamField()
        params = "number: Integer->default: 12"
        parsed = pf.clean(params, None)
        self.assertIsInstance(parsed, ParamDict)
        self.assertIsInstance(parsed["number"], IntegerParam)
        self.assertEqual(parsed["number"].default, 12)

    def test_form_construction(self):
        pf = ParamField()
        params = "number: Integer->default: 12"
        parsed = pf.clean(params, None)
        form = parsed.form()
        self.assertIsInstance(form, ParamInputForm)

    def test_file_support(self):
        # TODO: Test against file params when implemented
        pf = ParamField(file_support=False)
        params = "number: Integer->default: 12"
        parsed = pf.clean(params, None)

    # TODO: More test 
