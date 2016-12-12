from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch
from param_field.parser import parse_fields
from param_field.params import ParamDict
from param_field.forms import ParamInputForm
from param_field.params import *

from decimal import Decimal



class TestParamInputForm(TestCase):

    def test_field_param_validation(self):
        """Test fields call param validation function to validate
        input values"""
        d = ParamDict("""number:Integer->min:33""")

        form_data = {'number': 44 }
        form = ParamInputForm(params=d, data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {'number': 12}
        form = ParamInputForm(params=d, data=form_data)
        self.assertFalse(form.is_valid())
 
        # Test param object validation is called
        with patch.object(IntegerParam, 'validate') as mockval:
            self.assertEqual(mockval.call_count, 0)

            form_data = {'number': 44}
            form = ParamInputForm(params=d, data=form_data)
            self.assertTrue(form.is_valid())

            self.assertEqual(mockval.call_count, 1)

        with patch.object(IntegerParam, 'validate') as mockval:
            mockval.side_effect = ValidationError('')
            self.assertEqual(mockval.call_count, 0)

            form_data = {'number': 44}
            form = ParamInputForm(params=d, data=form_data)
            self.assertFalse(form.is_valid())

            self.assertEqual(mockval.call_count, 1)

    def test_error_message(self):
        """Test ValidationError message is used as the form's
        error message when validation fails"""
        d = ParamDict("""number:Integer->min:10""")
        
        with patch.object(IntegerParam, 'validate') as mockval:
            mockval.side_effect = ValidationError('12345asdf6789')
            self.assertEqual(mockval.call_count, 0)

            form_data = {'number': 44}
            form = ParamInputForm(params=d, data=form_data)
            self.assertFalse(form.is_valid())

            self.assertEqual(mockval.call_count, 1)
            self.assertTrue('12345asdf6789' in form.as_p())

    def test_type_validation(self):
        
        # Integer
        d = ParamDict("number:Integer->min:12 max:32")
        form = ParamInputForm(params=d, data={'number':'20'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['number'], int)
        self.assertEqual(form.cleaned_data['number'], 20)
 
        # Decimal
        d = ParamDict("number:Decimal->min:12.0 max:32.0")
        form = ParamInputForm(params=d, data={'number':'20'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['number'], Decimal)
        self.assertEqual(form.cleaned_data['number'], 20)

        # Dimmension
        d = ParamDict("number:Dimmension->min:12.0 max:32.0")
        form = ParamInputForm(params=d, data={'number':'20'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['number'], Decimal)
        self.assertEqual(form.cleaned_data['number'], 20)

        # Bool
        d = ParamDict("enable:Bool")
        form = ParamInputForm(params=d, data={'enable': 'true'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['enable'], bool)
        self.assertEqual(form.cleaned_data['enable'], True)

        # Text
        d = ParamDict("name:Text")
        form = ParamInputForm(params=d, data={'name': 'some name'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['name'], str)
        self.assertEqual(form.cleaned_data['name'], 'some name')

        # TextArea
        d = ParamDict("name:TextArea")
        form = ParamInputForm(params=d, data={'name': 'some name'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['name'], str)
        self.assertEqual(form.cleaned_data['name'], 'some name')

    def test_required_params(self):
        """Test parameters without a default value are required"""
        # Integer
        d = ParamDict("number:Integer")
        form = ParamInputForm(params=d, data={})
        self.assertFalse(form.is_valid())
        
        d = ParamDict("number:Integer->default:12")
        form = ParamInputForm(params=d, data={})
        self.assertTrue(form.is_valid())

        # Decimal
        d = ParamDict("number:Decimal")
        form = ParamInputForm(params=d, data={})
        self.assertFalse(form.is_valid())

        d = ParamDict("number:Decimal->default:13.2")
        form = ParamInputForm(params=d, data={})
        self.assertTrue(form.is_valid())

        # Dimmension
        d = ParamDict("number:Dimmension")
        form = ParamInputForm(params=d, data={})
        self.assertFalse(form.is_valid())

        d = ParamDict("number:Dimmension->default:13.2")
        form = ParamInputForm(params=d, data={})
        self.assertTrue(form.is_valid())

        # Text
        d = ParamDict("name: Text")
        form = ParamInputForm(params=d, data={})
        self.assertFalse(form.is_valid())

        d = ParamDict('name: Text->default:"2asdf"')
        form = ParamInputForm(params=d, data={})
        self.assertTrue(form.is_valid())

        # TextArea
        d = ParamDict("name: TextArea")
        form = ParamInputForm(params=d, data={})
        self.assertFalse(form.is_valid())

        d = ParamDict('name: TextArea->default:"2asdf"')
        form = ParamInputForm(params=d, data={})
        self.assertTrue(form.is_valid())

    def test_hidden_params(self):
        """Test invisible params are not present in the form"""
        d = ParamDict("""
                number_holes:Integer->min:33
                enable:Bool->default:False hidden:True""")

        form_data = {'number_holes': 44 }
        form = ParamInputForm(params=d)
        self.assertTrue('number_holes' in form.as_p())
        self.assertTrue('enable' in form.as_p())
    
        form_data = {'number_holes': 44, 'enable':True}
        form = ParamInputForm(params=d, data=form_data)
        self.assertTrue('number_holes' in form.as_p())
        self.assertTrue('enable' in form.as_p())
        self.assertTrue('hidden' in form.as_p())
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['number_holes'], 44)
        self.assertEqual(form.cleaned_data['enable'], True)
        
        form_data = {'number_holes': 44, 'enable':True}
        form = ParamInputForm(params=d, data=form_data)
        self.assertTrue('number_holes' in form.as_p())
        self.assertTrue('enable' in form.as_p())
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data), 2)
        self.assertEqual(form.cleaned_data['number_holes'], 44)

    def test_labels_from_name(self):
        """Test a label is generated for each field using field name"""
        d = ParamDict("""
                number_of_holes:Integer->min:33
                enable:Bool->default:False hidden:True""")

        form = ParamInputForm(params=d)
        self.assertTrue('Number of holes' in form.as_p())
        self.assertTrue('enable' in form.as_p())
    
    def test_choices_present(self):
        """Test param choices are present in form"""
        d = ParamDict('name:Text->choices:["445566", "yyttuu"]')
        
        form = ParamInputForm(params=d)
        self.assertTrue('445566' in form.as_p())
        self.assertTrue('yyttuu' in form.as_p())

    def test_choices_restriction(self):
        """ """
        # Text
        d = ParamDict('a_name: Text->choices:["aa", "bb", "cc"]')
        
        for s in ('aa', 'bb', 'cc'):
            form = ParamInputForm(params=d, data={'a_name': s})
            self.assertTrue(form.is_valid())

        for s in ('dd', 'ee', 'ff'):
            form = ParamInputForm(params=d, data={'a_name': s})
            self.assertFalse(form.is_valid())
        
        # Integer
        d = ParamDict('holes: Integer->choices: [12, 33, 44]')
       
        for s in (12, 33, 44):
            form = ParamInputForm(params=d, data={'holes': s})
            self.assertTrue(form.is_valid())

        for s in (11, -1, 88):
            form = ParamInputForm(params=d, data={'holes': s})
            self.assertFalse(form.is_valid())
       
        # Decimal
        d = ParamDict('width: Decimal->choices: [23.4, 44.3, 55.3]')

        for s in (Decimal('23.4'), Decimal('44.3'), Decimal('55.3')):
            form = ParamInputForm(params=d, data={'width': s})
            self.assertTrue(form.is_valid())
        
        for s in (Decimal('-23.4'), Decimal('14.3'), Decimal('55.4')):
            form = ParamInputForm(params=d, data={'width': s})
            self.assertFalse(form.is_valid())

        # Dimmension 
        d = ParamDict('width: Dimmension->choices: [23.4, 44.3, 55.3]')

        for s in (Decimal('23.4'), Decimal('44.3'), Decimal('55.3')):
            form = ParamInputForm(params=d, data={'width': s})
            self.assertTrue(form.is_valid())
        
        for s in (Decimal('-23.4'), Decimal('14.3'), Decimal('55.4')):
            form = ParamInputForm(params=d, data={'width': s})
            self.assertFalse(form.is_valid())


