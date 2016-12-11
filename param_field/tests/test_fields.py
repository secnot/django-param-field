from django.test import TestCase
from django.core.exceptions import ValidationError
from param_field.models import ParamField
from param_field.params import *


class TestParamField(TestCase):

    def test_params_are_parsed(self):
        p = ParamField()

        # Empty value
        v = p.clean('', None)
        self.assertEqual(len(v), 0)

        # One liner
        v = p.clean('''lines: Integer-> default:12 max:44 
                label:"number of lines"''', None)
        self.assertIsInstance(v, ParamDict)
        self.assertIsInstance(v['lines'], IntegerParam)
        self.assertEqual(v['lines'].default, 12)
        self.assertEqual(v['lines'].max, 44)
        self.assertEqual(v['lines'].label, 'number of lines')

        with self.assertRaises(ValidationError):
            p.clean('invalid-name:Bool', None)

        with self.assertRaises(ValidationError):
            p.clean('invalid_name:Invalidparam', None)

        with self.assertRaises(ValidationError):
            p.clean('invalid_property:Bool-> color:"red"', None)
        
        with self.assertRaises(ValidationError):
            p.clean('invalid_property_value:Bool-> default:"red"', None)
        
        # Two liner
        v = p.clean("""number_holes:Integer->default:12
                activate: Bool""", None)
        self.assertIsInstance(v, ParamDict)
        self.assertIsInstance(v['number_holes'], IntegerParam)
        self.assertIsInstance(v['activate'], BoolParam)
        self.assertEqual(v['number_holes'].default, 12)


    def test_errors_detected(self):

        p = ParamField()

        with self.assertRaises(ValidationError):
            p.clean('holes: Integer->default:99999999999', None)

        with self.assertRaises(ValidationError):
            p.clean('width: Decimal->default:2', None)

        with self.assertRaises(ValidationError):
            p.clean('widht: Dimmension->default:-3.4', None)
