from django.test import TestCase
from django.core.exceptions import ValidationError
from param_field.validators import ParamValidator

class TestParamValidator(TestCase):

    def test_validator(self):
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

    def test_fk_support_disabled(self):
        # TODO: No FK support yet
        pass
