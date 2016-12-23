from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch
from param_field.params import *
from param_field.forms import ParamInputForm
from param_field.conf import settings
from decimal import Decimal

class TestParamDict(TestCase):

    def test_param_count(self): 
        """Test len returns correct parameter number"""
        d = ParamDict("""
            bool:Bool->default:True label:"enable"
            int:Integer->default:44 label:"number of holes" """)
        self.assertEqual(len(d), 2)
 
        d = ParamDict(""" """)
        self.assertEqual(len(d), 0)

    def test_validate(self):
        p1 = BoolParam(default=True, label="enable")
        p2 = IntegerParam(default=44, label="number of holes")
        d = ParamDict("""
            bool: Bool-> default:True label:"enable"
            int: Integer-> default:44 label:"number of holes" """)
      
        # Control group
        d.validate({'bool': True, 'int': 12})

        # Test fields with a default value are not required
        d.validate({'bool': False})
        d.validate({'int': 34})
        d.validate({})
        
        # Test invalid values raise Validation exception
        with self.assertRaises(ValidationError):
            d.validate({'bool': 12})
        with self.assertRaises(ValidationError):
            d.validate({'bool': 'True'})
        with self.assertRaises(ValidationError):
            d.validate({'int': True})
        with self.assertRaises(ValidationError):
            d.validate({'int': Decimal('12')})

        # Test against params with some restriction
        d = ParamDict("""
            int_odd:Integer->odd:True
            int:Integer->default:44 max:55 label:"number of holes" """)

        d.validate({'int':55, 'int_odd': 45})
        d.validate({'int_odd': 1})

        with self.assertRaises(ValidationError):
            d.validate({'int_odd': 4})

        with self.assertRaises(ValidationError):
            d.validate({'int_odd': 1, 'int': 56})

        with self.assertRaises(ValidationError):
            d.validate({})

    def test_add_defaults(self):
        """Test add_defaults method"""
        d = ParamDict("""
            bool:Bool->default:True label:"enable"
            int:Integer->default:44 label:"number of holes" """)
      
        with_d = d.add_defaults({})
        self.assertEqual(with_d['bool'], True)
        self.assertEqual(with_d['int'], 44)
        
        with_d = d.add_defaults({'int': 33, 'bool':False})
        self.assertEqual(with_d['bool'], False)
        self.assertEqual(with_d['int'], 33)
        
        d = ParamDict("""
            int_odd:Integer-> odd:True
            int:Integer-> default:44""")

        with_d = d.add_defaults({})
        self.assertEqual(with_d['int'], 44)
        self.assertTrue(len(with_d), 1)
        
    def test_serialize(self):
        # TODO: Test when file fields are implemented
        pass

    def test_deserialize(self):
        # TODO: Test when file fields are implemented
        pass

    def test_string_representation(self):
        
        # Empty dict mapped into empty string
        d = ParamDict()
        self.assertEqual(str(d), '')

        # Check original source preserved.
        field_def = """
            name:Bool-> default:True label:"the label" """
        d = ParamDict(field_def)

        self.assertEqual(str(d), field_def)
  
        # Two parameters check order preserved
        d = ParamDict("""
            bool:Bool->default:True label:"enable"
            int:Integer->default:44 label:"number of holes" """)

        self.assertTrue('Bool' in str(d))
        self.assertTrue('enable' in str(d))
        self.assertTrue('True' in str(d))
        self.assertTrue('Integer' in str(d))
       
        # Test rest of param types
        d = ParamDict("""
            p1: Decimal
            p2: Dimmension
            p3: Text
            p4: Text""")

        for name in ('p1', 'p2', 'p3', 'p4'):
            self.assertTrue(name in str(d))

    def test_form_generation(self): 

        # test ParamDict.form() generates a valid Form
        d = ParamDict("""
            name_12345:Bool-> default:True label:"the label" """)
        form = d.form()

        self.assertIsInstance(form, ParamInputForm)
        self.assertTrue('name_12345' in form.as_p())

        
        # Test empty Dict returns None instead of empty form
        d = ParamDict("")
        form = d.form()
        self.assertEqual(form, None)



class TestBaseParam(TestCase):


    def test_unknown_properties(self):
        """Test error raised when unsuported properties provided
        during creation"""
        param = TextParam(label='the_param', max_length=20)

        with self.assertRaises(ValueError):
            param=TextParam(label='the name', invented_param=43)

    def test_property_type(self):
        """Test properties type are checked"""

        # Common params
        TextParam(label='a label')
        with self.assertRaises(ValueError):
            TextParam(label=12)

        TextParam(help_text='some boring explanation')
        with self.assertRaises(ValueError):
            TextParam(help_text=12)

        IntegerParam(default=12)
        DecimalParam(default=Decimal('12'))
        DimmensionParam(default=Decimal('14'))
        TextParam(default='asdf')
        TextAreaParam(default='3')
        with self.assertRaises(ValueError):
            IntegerParam(default='12')
        with self.assertRaises(ValueError):
            DecimalParam(default=12)
        with self.assertRaises(ValueError):
            DimmensionParam(default=14)
        with self.assertRaises(ValueError):
            TextParam(default=2)
        with self.assertRaises(ValueError):
            TextAreaParam(default=3)
        
        DecimalParam(choices=[Decimal('34.2'), Decimal('44.0')])
        with self.assertRaises(ValueError):
            DecimalParam(choices=[23, Decimal('55.3')])
        with self.assertRaises(ValueError):
            DecimalParam(choices=["44.5"])
        with self.assertRaises(ValueError):
            DecimalParam(choices=Decimal("44.5"))

        IntegerParam(label="3434")
        with self.assertRaises(ValueError):
            IntegerParam(label=23)
        
        IntegerParam(help_text="some helpy text")
        with self.assertRaises(ValueError):
            IntegerParam(help_text=12)

        IntegerParam(hidden=False, default=22)
        with self.assertRaises(ValueError):
            IntegerParam(hidden=0)

        # String params
        TextParam(max_length=32)
        with self.assertRaises(ValueError):
            TextParam(max_length="32")

        TextAreaParam(min_length=3)
        with self.assertRaises(ValueError):
            TextAreaParam(min_length="3")
        
        # Numeric params
        DecimalParam(max=Decimal("43.4"))
        IntegerParam(max=23)
        with self.assertRaises(ValueError):
            DecimalParam(max='42')
        with self.assertRaises(ValueError):
            IntegerParam(max='2')

        # Integer params
        IntegerParam(odd=True)
        IntegerParam(even=True)
        with self.assertRaises(ValueError):
            IntegerParam(odd=12)
        with self.assertRaises(ValueError):
            IntegerParam(even="12")

    def test_property_limits(self):
        """Test properties limit values default, choices"""
        TextParam(label="a"*settings.PARAM_LABEL_MAX_LENGTH)
        with self.assertRaises(ValueError):
            TextParam(label="b"*(settings.PARAM_LABEL_MAX_LENGTH+1))

        TextParam(help_text="b"*settings.PARAM_HELP_TEXT_MAX_LENGTH)
        with self.assertRaises(ValueError):
            TextParam(help_text="c"*(settings.PARAM_HELP_TEXT_MAX_LENGTH+1))

        IntegerParam(default=settings.PARAM_INT_MAX)
        with self.assertRaises(ValueError):
            IntegerParam(default=settings.PARAM_INT_MAX+1)
        IntegerParam(default=settings.PARAM_INT_MIN)
        with self.assertRaises(ValueError):
            IntegerParam(default=settings.PARAM_INT_MIN-1)

        DecimalParam(choices=[Decimal('12'), settings.PARAM_DECIMAL_MAX])
        with self.assertRaises(ValueError):
            IntegerParam(choices=[Decimal('12'), settings.PARAM_DECIMAL_MAX+1])

        DecimalParam(choices=[Decimal('12'), settings.PARAM_DECIMAL_MIN])
        with self.assertRaises(ValueError):
            IntegerParam(choices=[Decimal('12'), settings.PARAM_DECIMAL_MIN-1])

        TextParam(default="a"*settings.PARAM_TEXT_MAX_LENGTH)
        with self.assertRaises(ValueError):
            TextParam(default="b"*(settings.PARAM_TEXT_MAX_LENGTH+1))

    def test_get_choices(self):
        """Test returns choice-name pair list"""
        p = IntegerParam(choices=[12, 34])
        self.assertEqual(p.get_choices(), [(12, '12'), (34, '34')])

    def test_restrinctions(self):
        TextParam(default="asdf", choices=["asdf", "1234"])
        with self.assertRaises(ValueError):
            TextParam(default="asdf", choices=["1234", "4567"])
        
        IntegerParam(default=13, choices=[12, 13, 14])
        with self.assertRaises(ValueError):
            TextParam(default=13, choices=[12, 14])

        DecimalParam(default=Decimal('12'), choices=[Decimal('12')])
        with self.assertRaises(ValueError):
            DecimalParam(default=Decimal('12'), choices=[Decimal('13')])
        with self.assertRaises(ValueError):
            DecimalParam(default=13, choices=[Decimal('13')])

        # Test label and help_text max_length
        DecimalParam(label='a'*settings.PARAM_LABEL_MAX_LENGTH)
        DecimalParam(help_text='b'*settings.PARAM_HELP_TEXT_MAX_LENGTH)
        with self.assertRaises(ValueError):
            DecimalParam(label='a'*(settings.PARAM_LABEL_MAX_LENGTH+1))
        with self.assertRaises(ValueError):
            DecimalParam(help_text='b'*(settings.PARAM_HELP_TEXT_MAX_LENGTH+1))

    def test_label_help(self):
        """Test label and help_text"""
        b = BoolParam()
        self.assertEqual(b.label, '')
        self.assertEqual(b.help_text, '')

        b = BoolParam(label="asd", help_text="help")
        self.assertEqual(b.label, 'asd')
        self.assertEqual(b.help_text, 'help')

    def test_choices_empty_list(self):
        """Test choices list must contain at least one element"""
        b = IntegerParam(choices=[])

    def test_to_str(self):
        """ """
        self.assertEqual(BoolParam().to_str(), 'Bool')
        self.assertEqual(IntegerParam().to_str(), 'Integer')
        self.assertEqual(DecimalParam().to_str(), 'Decimal')
        self.assertEqual(DimmensionParam().to_str(), 'Dimmension')
        self.assertEqual(TextParam().to_str(), 'Text')

        p = BoolParam(label='the name')
        self.assertEqual(p.to_str(), 'Bool-> label:"the name"')

        p = BoolParam(help_text='the helpy help')
        self.assertEqual(p.to_str(), 'Bool-> help_text:"the helpy help"')

        p = BoolParam(default=False)
        self.assertEqual(p.to_str(), 'Bool-> default:False')
        
        p = BoolParam(default=True)
        self.assertEqual(p.to_str(), 'Bool-> default:True')

        p = BoolParam(default=True, hidden=False)
        self.assertEqual(p.to_str(), 'Bool-> default:True')

        p = DecimalParam(min=Decimal('12.0'), max=Decimal('20.4'))
        self.assertEqual(p.to_str(), 'Decimal-> min:12.0 max:20.4')

        p = TextParam(max_length=20, min_length=1)
        self.assertEqual(p.to_str(), 'Text-> min_length:1 max_length:20')

        p = DimmensionParam(default=Decimal('12.2'))
        self.assertEqual(p.to_str(), 'Dimmension-> default:12.2')

        p = IntegerParam(even=True, odd=True)
        self.assertEqual(p.to_str(), 'Integer-> even:True odd:True')

        #Choices
        p = IntegerParam(choices=[1, 2, 3])
        self.assertEqual(p.to_str(), 'Integer-> choices:[1, 2, 3]')

        p = TextParam(choices=["a", "b", "c"])
        self.assertEqual(p.to_str(), 'Text-> choices:["a", "b", "c"]')

        p = DecimalParam(choices=[Decimal("1.2"), Decimal("2.5")])
        self.assertEqual(p.to_str(), 'Decimal-> choices:[1.2, 2.5]')

        p = DimmensionParam(choices=[Decimal("0.0")])
        self.assertEqual(p.to_str(), 'Dimmension-> choices:[0.0]')

        # String escaping
        p = TextParam(default='asdf\n123"')
        self.assertEqual(p.to_str(), '''Text-> default:"asdf\\n123\\""''')

    def test_is_valid(self):
        """Just test it calls validate method, more test with each
        param subclass"""
        with patch.object(Param, 'validate') as mockmeth:
            p = IntegerParam()

            # Validation Error
            mockmeth.side_effect = ValidationError('Invalid value')
            self.assertFalse(p.is_valid(12))
            self.assertEqual(mockmeth.call_count, 1)

            mockmeth.side_effect = None
            self.assertTrue(p.is_valid(12))
            self.assertTrue(p.is_valid("no validation"))
            self.assertEqual(mockmeth.call_count, 3)

        with patch.object(Param, 'validate') as mockmeth:
            p = IntegerParam()
            # Type Error
            mockmeth.side_effect = TypeError('Invalid type')
            self.assertFalse(p.is_valid(12))
            self.assertEqual(mockmeth.call_count, 1)

            mockmeth.side_effect = None
            self.assertTrue(p.is_valid(12))
            self.assertTrue(p.is_valid("no validation"))
            self.assertEqual(mockmeth.call_count, 3)

        with patch.object(Param, 'validate') as mockmeth:
            p = IntegerParam()
            # Value Error 
            mockmeth.side_effect = ValueError('Invalid type')
            self.assertFalse(p.is_valid(12))
            self.assertEqual(mockmeth.call_count, 1)

            mockmeth.side_effect = None
            self.assertTrue(p.is_valid(12))
            self.assertTrue(p.is_valid("no validation"))
            self.assertEqual(mockmeth.call_count, 3)

    def test_validate(self):
        # Test checks type
        p = BoolParam()
        p.validate(True)
        with self.assertRaises(TypeError):
            p.validate(12)

        # Test call custom properties validators
        with patch.object(IntegerParam, '_validate_min') as mock_min:
            p = IntegerParam()
            self.assertEqual(mock_min.call_count, 0)
            p.validate(12)
            self.assertEqual(mock_min.call_count, 1)

            mock_min.side_effect = ValidationError('invalid value')
            with self.assertRaises(ValidationError):
                p.validate(12)

    def test_hidden(self):
        """Test hidden parameters require default value"""
        IntegerParam(hidden=True, default=12)
        with self.assertRaises(ValueError):
            IntegerParam(hidden=True)

        DecimalParam(hidden=True, default=Decimal('23.3'))
        with self.assertRaises(ValueError):
            DecimalParam(hidden=True)

        DimmensionParam(hidden=True, default=Decimal('4'))
        with self.assertRaises(ValueError):
            DimmensionParam(hidden=True)
       
        BoolParam(hidden=True, default=True)
        with self.assertRaises(ValueError):
            BoolParam(hidden=True)

        TextParam(hidden=True, default="adfasd")
        with self.assertRaises(ValueError):
            TextParam(hidden=True)

        TextAreaParam(hidden=True, default="asdf")
        with self.assertRaises(ValueError):
            TextAreaParam(hidden=True)

        # TODO: Test choices are ignored when field is hidden


class TestBoolParam(TestCase):
    
    def test_unsupported_properties(self):
        """Test properties not supported by bool"""
        with self.assertRaises(ValueError):
            BoolParam(choices=[True, False])
        with self.assertRaises(ValueError):
            BoolParam(max=12)
        with self.assertRaises(ValueError):
            BoolParam(max=True)
        with self.assertRaises(ValueError):
            BoolParam(min=13)
        with self.assertRaises(ValueError):
            BoolParam(odd=True)
        with self.assertRaises(ValueError):
            BoolParam(even=True)
        with self.assertRaises(ValueError):
            BoolParam(max_length=30)
        with self.assertRaises(ValueError):
            BoolParam(min_length=1)
        with self.assertRaises(ValueError):
            BoolParam(max_digits=5)
        with self.assertRaises(ValueError):
            BoolParam(max_decimals=2)

    def test_is_valid(self):
        p = BoolParam(default=False)

        self.assertTrue(p.is_valid(True))
        self.assertTrue(p.is_valid(False))

        self.assertFalse(p.is_valid(None))
        self.assertFalse(p.is_valid(12))
        self.assertFalse(p.is_valid("23"))
        self.assertFalse(p.is_valid(0))
        self.assertFalse(p.is_valid(1))

        p = BoolParam()
        self.assertTrue(p.is_valid(True))
        self.assertTrue(p.is_valid(False))
        self.assertFalse(p.is_valid(None))


class TestTextParam(TestCase):

    param = TextParam
    def test_unsupported_properties(self):
        with self.assertRaises(ValueError):
            self.param(max=12)
        with self.assertRaises(ValueError):
            self.param(min=10)
        with self.assertRaises(ValueError):
            self.param(odd=True)
        with self.assertRaises(ValueError):
            self.param(even=True)

    def test_restrictions(self):
        """ """
        self.param(max_length=9, min_length=2, default="12")
        self.param(max_length=9, min_length=2, default="123456789")
        self.param(max_length=9, min_length=2, default="12",
                choices=["12", "123", "123456789"])

        with self.assertRaises(ValueError):
            self.param(max_length=9, min_length=2, default="1")
        with self.assertRaises(ValueError):
            self.param(max_length=9, min_length=2, default="1234567890")
        with self.assertRaises(ValueError):
            self.param(max_length=9, min_length=2, choices=["1", "123"])
        with self.assertRaises(ValueError):
            self.param(max_length=9, min_length=2, choices=["12", "1234567890"])
        with self.assertRaises(ValueError):
            self.param(min_length=-1)
        with self.assertRaises(ValueError):
            self.param(max_length=-1)
        with self.assertRaises(ValueError):
            self.param(max_length=11, min_length=12)

    def test_max_length_property_limits(self):
        """Test absolute limits set in config for the properties
        are used"""
        self.param(max_length=settings.PARAM_TEXT_MAX_LENGTH)
        with self.assertRaises(ValueError):
            self.param(max_length=settings.PARAM_TEXT_MAX_LENGTH+1)

    def test_is_valid(self):
        p = self.param(min_length=3,)
        self.assertTrue(p.is_valid("1234"))
        self.assertTrue(p.is_valid("123"))

        self.assertFalse(p.is_valid("12"))
        self.assertFalse(p.is_valid(12))
        self.assertFalse(p.is_valid(False))
        self.assertFalse(p.is_valid(""))
        self.assertFalse(p.is_valid(None))
        
        p = TextParam(min_length=4, default="12345")
        self.assertFalse(p.is_valid(None))



class TestTextAreaParam(TestTextParam):
    param=TextAreaParam


class TestIntegerParam(TestCase):
   
    def test_unsupported_properties(self):
        with self.assertRaises(ValueError):
            IntegerParam(max_length=12)
        with self.assertRaises(ValueError):
            IntegerParam(min_length=44)
        with self.assertRaises(ValueError):
            IntegerParam(max_digits=5)
        with self.assertRaises(ValueError):
            IntegerParam(max_decimals=2)

    def test_restrictions(self):
        """Test provided parameter restrictions are applied to
        accepted values"""
        IntegerParam(default=12)
        with self.assertRaises(ValueError):
            IntegerParam(min=13, default=12)
        with self.assertRaises(ValueError):
            IntegerParam(min=13, choices=[11, 14])

        IntegerParam(max = 12, default=12)
        with self.assertRaises(ValueError):
            IntegerParam(max=11, default=12)
        with self.assertRaises(ValueError):
            IntegerParam(max=11, default=[12, 1])
  
        IntegerParam(odd=True, default=11)
        with self.assertRaises(ValueError):
            IntegerParam(odd=True, default=2)
        with self.assertRaises(ValueError):
            IntegerParam(odd=True, choices=[4])

        IntegerParam(even=True, default=12)
        with self.assertRaises(ValueError):
            IntegerParam(even=True, default=1)

        # Property combination
        with self.assertRaises(ValueError):
            IntegerParam(even=True, odd=True, default=2)
        with self.assertRaises(ValueError):
            IntegerParam(even=True, odd=True, default=1)

        IntegerParam(max=12, min=10, default=11)
        IntegerParam(max=11, min=11, default=11)
        with self.assertRaises(ValueError):
            IntegerParam(max=12, min=10, default=13)
        with self.assertRaises(ValueError):
            IntegerParam(max=12, min=10, default=9)

        IntegerParam(max=13, odd=True, default=13)
        with self.assertRaises(ValueError):
            IntegerParam(max=13, odd=True, default=15)
        with self.assertRaises(ValueError):
            IntegerParam(max=13, odd=True, default=8)
        
        # Crossing max/min values
        with self.assertRaises(ValueError):
            IntegerParam(max=12, min=13)
 
    def test_absolute_property_limits(self):
        """Test absolute limits set in config for the properties
        are used"""
        IntegerParam(default=settings.PARAM_INT_MAX)
        IntegerParam(default=settings.PARAM_INT_MIN)
        with self.assertRaises(ValueError):
            IntegerParam(default=settings.PARAM_INT_MAX+1)
        with self.assertRaises(ValueError):
            IntegerParam(default=settings.PARAM_INT_MIN-1)

    def test_is_valid(self):
        p = IntegerParam(max=12)
        self.assertTrue(p.is_valid(12))
        self.assertFalse(p.is_valid(14))

        p = IntegerParam(max=13, min=12)
        self.assertTrue(p.is_valid(13))
        self.assertTrue(p.is_valid(12))
        self.assertFalse(p.is_valid(11))
        self.assertFalse(p.is_valid(14))

        p = IntegerParam(choices=[12, 45, 33])
        self.assertTrue(p.is_valid(12))
        self.assertTrue(p.is_valid(45))
        self.assertTrue(p.is_valid(33))
        self.assertFalse(p.is_valid(13))

        p = IntegerParam(odd=True)
        self.assertTrue(p.is_valid(11))
        self.assertFalse(p.is_valid(-2))

        p = IntegerParam(even=True, max=30)
        self.assertTrue(p.is_valid(28))
        self.assertTrue(p.is_valid(30))
        self.assertFalse(p.is_valid(32))
        self.assertFalse(p.is_valid(23))
        self.assertFalse(p.is_valid(None))

        p = IntegerParam(default=12)
        self.assertFalse(p.is_valid(None))



class TestDecimalParam(TestCase):
    #TODO:
    def test_unsupported_properties(self):
        with self.assertRaises(ValueError):
            DecimalParam(max_length=12)
        with self.assertRaises(ValueError):
            DecimalParam(min_length=1)
        with self.assertRaises(ValueError):
            DecimalParam(odd=False)
        with self.assertRaises(ValueError):
            DecimalParam(even=False)

    def test_restrictions(self):
 
        DecimalParam(default=Decimal("12"))
        with self.assertRaises(ValueError):
            DecimalParam(min=Decimal("13"), default=Decimal("12"))
        with self.assertRaises(ValueError):
            DecimalParam(min=Decimal("13"), 
                    choices=[Decimal("11"), Decimal("14")])

        DecimalParam(max=Decimal("12"), default=Decimal("-12"))
        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("11"), default=Decimal("12"))
        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("11"), 
                    default=[Decimal("12"), Decimal("1")])
 
        # Choices 
        DecimalParam(max=Decimal("12"), choices=[Decimal("1"), Decimal("2")],
            default=Decimal("1"))

        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("12"), choices=[Decimal("1"), Decimal("2")],
                default=Decimal("3"))

        # Property combination
        DecimalParam(max=Decimal("12"), min=Decimal("10"), 
                default=Decimal("11"))
        DecimalParam(max=Decimal("11"), min=Decimal("11"), 
                default=Decimal("11"))
        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("12"), min=Decimal("10"), 
                    default=Decimal("13"))
        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("12"), min=Decimal("10"), 
                    default=Decimal("9"))

        # Crossing max/min values
        with self.assertRaises(ValueError):
            DecimalParam(max=Decimal("12"), min=Decimal("13"))

        # Max/min value has too many digits/decimals
        with self.assertRaises(ValueError):
            DecimalParam(max_digits=5, max=Decimal('999999'))
        with self.assertRaises(ValueError):
            DecimalParam(max_decimals=2, min=Decimal('44.999'))

        # Test max_decimals must be smaller or equal to max_digits
        DecimalParam(max_digits=2, max_decimals=2)
        with self.assertRaises(ValueError):
            DecimalParam(max_digits=2, max_decimals=3)

        # Types
        with self.assertRaises(ValueError):
            DecimalParam(max=12)
        with self.assertRaises(ValueError):
            DecimalParam(max=False)
        with self.assertRaises(ValueError):
            DecimalParam(max=None)
        with self.assertRaises(ValueError):
            DecimalParam(max="33")
 
        with self.assertRaises(ValueError):
            DecimalParam(min=12)
        with self.assertRaises(ValueError):
            DecimalParam(min=False)
        with self.assertRaises(ValueError):
            DecimalParam(min=None)
        with self.assertRaises(ValueError):
            DecimalParam(min="33")

        with self.assertRaises(ValueError):
            DecimalParam(max_digits=Decimal("33"))
        with self.assertRaises(ValueError):
            DecimalParam(max_decimals=Decimal("333"))
    def test_absolute_property_limits(self):
        """Test absolute limits set in config for the properties
        are used"""
        # Default restriction
        DecimalParam(max=settings.PARAM_DECIMAL_MAX)
        DecimalParam(max=settings.PARAM_DECIMAL_MIN)
        DecimalParam(min=settings.PARAM_DECIMAL_MIN)
        DecimalParam(min=settings.PARAM_DECIMAL_MAX)
        DecimalParam(max_digits=settings.PARAM_DECIMAL_MAX_DIGITS)
        DecimalParam(max_digits=1)
        DecimalParam(max_decimals=settings.PARAM_DECIMAL_MAX_DECIMALS)
        DecimalParam(max_decimals=0)

        with self.assertRaises(ValueError):
            DecimalParam(max=settings.PARAM_DECIMAL_MAX+1)
        with self.assertRaises(ValueError):
            DecimalParam(max=settings.PARAM_DECIMAL_MIN-1)
        with self.assertRaises(ValueError):
            DecimalParam(min=settings.PARAM_DECIMAL_MIN-1)
        with self.assertRaises(ValueError):
            DecimalParam(min=settings.PARAM_DECIMAL_MAX+1)
        with self.assertRaises(ValueError):
            DecimalParam(max_digits=settings.PARAM_DECIMAL_MAX_DIGITS+1)
        with self.assertRaises(ValueError):
            DecimalParam(max_digits=0)
        with self.assertRaises(ValueError):
            DecimalParam(max_decimals=settings.PARAM_DECIMAL_MAX_DECIMALS+1)
        with self.assertRaises(ValueError):
            DecimalParam(max_decimals=-1)

    def test_is_valid(self):
        p = DecimalParam(max=Decimal("44"))
        self.assertTrue(p.is_valid(Decimal("12")))
        self.assertTrue(p.is_valid(Decimal("-12")))

        self.assertFalse(p.is_valid(Decimal("555")))
        self.assertFalse(p.is_valid(None))
        self.assertFalse(p.is_valid(12))
        self.assertFalse(p.is_valid("sdf"))
        self.assertFalse(p.is_valid(True))

        p = DecimalParam(max=Decimal("44"), default=Decimal("22"))
        self.assertFalse(p.is_valid(None))

        # decimals and digit restrictions
        p = DecimalParam(max_digits=4, max_decimals=2)
        self.assertTrue(p.is_valid(Decimal("22.22")))
        self.assertTrue(p.is_valid(Decimal("2.22")))
        self.assertTrue(p.is_valid(Decimal("1111")))
        self.assertFalse(p.is_valid(Decimal("2.222")))
        self.assertFalse(p.is_valid(Decimal("22222")))


class TestDimmensionParam(TestCase):
    
    def test_unsupported_properties(self):
        with self.assertRaises(ValueError):
            DimmensionParam(max_length=12)
        with self.assertRaises(ValueError):
            DimmensionParam(min_length=1)
        with self.assertRaises(ValueError):
            DimmensionParam(odd=False)
        with self.assertRaises(ValueError):
            DimmensionParam(even=False)

    def test_always_positive(self):
        p = DimmensionParam()
        self.assertTrue(p.is_valid(Decimal("0")))
        self.assertFalse(p.is_valid(Decimal("-1")))

        with self.assertRaises(ValueError):
            p = DimmensionParam(min=Decimal("-1"))
 
    def test_restrictions(self): 
        DimmensionParam(default=Decimal("12"))
        with self.assertRaises(ValueError):
            DimmensionParam(min=Decimal("13"), default=Decimal("12"))
        with self.assertRaises(ValueError):
            DimmensionParam(min=Decimal("13"), 
                    choices=[Decimal("11"), Decimal("14")])

        DimmensionParam(max=Decimal("12"), default=Decimal("1"))
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("11"), default=Decimal("12"))
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("11"), 
                    default=[Decimal("12"), Decimal("1")])
  
        # Property combination
        DimmensionParam(max=Decimal("12"), min=Decimal("10"), 
                default=Decimal("11"))
        DimmensionParam(max=Decimal("11"), min=Decimal("11"), 
                default=Decimal("11"))
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("12"), min=Decimal("10"), 
                    default=Decimal("13"))
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("12"), min=Decimal("10"), 
                    default=Decimal("9"))

        # Crossing max/min values
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("12"), min=Decimal("13"))

        # Test max_decimals must be smaller or equal to max_digits
        DecimalParam(max_digits=2, max_decimals=2)
        with self.assertRaises(ValueError):
            DecimalParam(max_digits=2, max_decimals=3)

        # Types
        with self.assertRaises(ValueError):
            DimmensionParam(max=12)
        with self.assertRaises(ValueError):
            DimmensionParam(max=False)
        with self.assertRaises(ValueError):
            DimmensionParam(max=None)
        with self.assertRaises(ValueError):
            DimmensionParam(max="33")
 
        with self.assertRaises(ValueError):
            DimmensionParam(min=12)
        with self.assertRaises(ValueError):
            DimmensionParam(min=False)
        with self.assertRaises(ValueError):
            DimmensionParam(min=None)
        with self.assertRaises(ValueError):
            DimmensionParam(min="33")

    def test_absolute_property_limits(self):
        """Test absolute limits set in config for the properties
        are used"""
        DimmensionParam(max=settings.PARAM_DIMMENSION_MAX)
        DimmensionParam(max=Decimal("0"))
        DimmensionParam(min=settings.PARAM_DIMMENSION_MAX)
        DimmensionParam(min=Decimal("0"))
        DimmensionParam(max_digits=settings.PARAM_DIMMENSION_MAX_DIGITS)
        DimmensionParam(max_digits=1)
        DimmensionParam(max_decimals=settings.PARAM_DIMMENSION_MAX_DECIMALS)
        DimmensionParam(max_decimals=0)
        with self.assertRaises(ValueError):
            DimmensionParam(max=settings.PARAM_DIMMENSION_MAX+1)
        with self.assertRaises(ValueError):
            DimmensionParam(max=Decimal("-1"))
        with self.assertRaises(ValueError):
            DimmensionParam(min=settings.PARAM_DIMMENSION_MAX+1)
        with self.assertRaises(ValueError):
            DimmensionParam(min=Decimal("-1"))
        with self.assertRaises(ValueError):
            DimmensionParam(max_digits=settings.PARAM_DIMMENSION_MAX_DIGITS+1)
        with self.assertRaises(ValueError):
            DimmensionParam(max_digits=0)
        with self.assertRaises(ValueError):
            DimmensionParam(max_decimals=settings.PARAM_DIMMENSION_MAX_DECIMALS+1)
        with self.assertRaises(ValueError):
            DimmensionParam(max_decimals=-1)


    def test_is_valid(self):
        p = DimmensionParam(max=Decimal("44"))
        self.assertTrue(p.is_valid(Decimal("12")))
        self.assertTrue(p.is_valid(Decimal("0")))

        self.assertFalse(p.is_valid(Decimal("-1")))
        self.assertFalse(p.is_valid(Decimal("555")))
        self.assertFalse(p.is_valid(None))
        self.assertFalse(p.is_valid(12))
        self.assertFalse(p.is_valid("sdf"))
        self.assertFalse(p.is_valid(True))

        p = DimmensionParam(max=Decimal("44"), default=Decimal("22"))
        self.assertFalse(p.is_valid(None))

        # decimals and digit restrictions
        p = DimmensionParam(max_digits=4, max_decimals=2)
        self.assertTrue(p.is_valid(Decimal("22.22")))
        self.assertTrue(p.is_valid(Decimal("2.22")))
        self.assertTrue(p.is_valid(Decimal("1111")))
        self.assertFalse(p.is_valid(Decimal("2.222")))
        self.assertFalse(p.is_valid(Decimal("22222")))






class TestFileParam(TestCase):    
    param = FileParam

    def test_unsupported_properties(self):
        with self.assertRaises(ValueError):
            self.param(max=12)
        with self.assertRaises(ValueError):
            self.param(min=10)
        with self.assertRaises(ValueError):
            self.param(odd=True)
        with self.assertRaises(ValueError):
            self.param(even=True)
        with self.assertRaises(ValueError):
            self.param(hidden=True)
        with self.assertRaises(ValueError):
            self.param(max_length=12)
        with self.assertRaises(ValueError):
            self.param(default=12)
        with self.assertRaises(ValueError):
            self.param(max_digits=5)
        with self.assertRaises(ValueError):
            self.param(max_decimals=2)

    def test_is_valid(self):
        p = TextParam(required=True)
        self.assertTrue(p.is_valid("fasd"))


