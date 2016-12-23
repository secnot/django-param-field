from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from param_field.models import ParamField
from param_field.params import *
from param_field.forms import *

from django.db import models


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

    def test_no_file_support(self):
        pf = ParamField(file_support=False)
        params = "number: Integer->default: 12"
        parsed = pf.clean(params, None)

        # File and Image not supported
        with self.assertRaises(ValidationError):
            params = "a_file: File"
            parsed = pf.clean(params, None)

        with self.assertRaises(ValidationError):
            params = "a_image: Image"
            parsed = pf.clean(params, None)

    def test_file_support(self):
        pf = ParamField(file_support=True)
        params = "number: Integer->default: 12"
        parsed = pf.clean(params, None)

        # File and Image supported
        params = "a_file: File"
        parsed = pf.clean(params, None)

        params = "a_image: Image"
        parsed = pf.clean(params, None)

    def test_custom_max_length(self):
        """Test user provided max_length is used"""
        p = ParamField(max_length=12)
       
        # Valid length 
        params = "number: Bool"
        valid = p.clean(params, None)

        # Too long
        p = ParamField(max_length=12)
        with self.assertRaises(ValidationError):
            params = "number1: Bool"
            invalid = p.clean(params, None)

    @override_settings(PARAM_FIELD_MAX_LENGTH=18)
    def test_default_max_length(self):
        # valid length
        p = ParamField()
        params = "enable_field: Bool"
        valid = p.clean(params, None)


        # Too long
        p = ParamField()
        params = "enable_field1: Bool"
        with self.assertRaises(ValidationError):
            valid = p.clean(params, None)
