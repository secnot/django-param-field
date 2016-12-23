from django.test import TestCase
from django.core.exceptions import ValidationError
from param_field.validators import ParamValidator, ParamLengthValidator
from param_field.params import ParamDict

class TestParamValidator(TestCase):

    def test_validator(self):
        """Test validator without file support"""
        validator = ParamValidator()

        # Control group
        input_str = """
            activate: Bool-> default:False
            message: Text-> min_length:2 max_length:20
        """
        validator(input_str)

        # Invalid parameter type (float)
        input_str = "activate: Float-> default: 3.23"
        with self.assertRaises(ValidationError):
            validator(input_str)

        # Invalid option type (default should be a bool)
        input_str = "does_not_compute: Bool->default:32"
        with self.assertRaises(ValidationError):
            validator(input_str)

        # Invalid name
        input_str = "half name: Integer-> default:55"
        with self.assertRaises(ValidationError):
            validator(input_str)

        # files not supported
        input_str = "upload: File"
        with self.assertRaises(ValidationError):
            validator(input_str)

    def test_file_validator(self):
        """Test validator with file support"""
        validator = ParamValidator(file_support=True)

        # files supported
        input_str = """
            upload: File
            enable: Bool"""
        validator(input_str)

        # Invalid control input
        input_str = "asdfasdf: Float"
        with self.assertRaises(ValidationError):
            validator(input_str)



class TestParamLengthValidator(TestCase):

    def test_validator(self):

        validator = ParamLengthValidator(15)

        # Short param
        validator(ParamDict("number: Integer"))

        # Long param
        with self.assertRaises(ValidationError):
            validator(ParamDict("number1: Integer"))

