from django.test import TestCase

from pyparsing import ParseBaseException, ParseException, ParseFatalException
from decimal import Decimal
from collections import OrderedDict

from param_field.parser import parse_fields
from param_field.params import *
from param_field.conf import settings


class TestParserBase(TestCase):

    def test_empty_string(self):
        p = parse_fields("")
        self.assertIsInstance(p, OrderedDict)
        self.assertEqual(len(p), 0)

        p = parse_fields("          \n")
        self.assertIsInstance(p, OrderedDict)
        self.assertEqual(len(p), 0)

    def test_param_type(self):
        
        # Test supported types
        parse_fields("width1:Dimmension")
        parse_fields("width2:Integer")
        parse_fields("width3:Decimal")
        parse_fields("width4:Text")
        parse_fields("widht5:TextArea")
        parse_fields("width6:Bool")

        parse_fields("width7:File", file_support=True)
        parse_fields("width8:Image", file_support=True)
       
        # Test file_support must be enabled for File and Image
        with self.assertRaises(ParseException):
            parse_fields("width: File")

        with self.assertRaises(ParseException):
            parse_fields("widht: Image")

        # Test unknown type
        with self.assertRaises(ParseException):
            parse_fields("width:CarNumber")
       
        # Test Type case sensitive
        with self.assertRaises(ParseException):
            parse_fields("width:dimmension")
        with self.assertRaises(ParseException):
            parse_fields("width:integer")
        with self.assertRaises(ParseException):
            parse_fields("width:decimal")
        with self.assertRaises(ParseException):
            parse_fields("width:text")
        with self.assertRaises(ParseException):
            parse_fields("width:textarea")
        with self.assertRaises(ParseException):
            parse_fields("width:bool")
        with self.assertRaises(ParseException):
            parse_fields("width:file", file_support=True)
        with self.assertRaises(ParseException):
            parse_fields("width:image", file_support=True)

    def test_correct_param_used(self):
        """Test correct param object is used for each type"""
        d = parse_fields('para: Integer')
        self.assertIsInstance(d['para'], IntegerParam)
        d = parse_fields('para: Decimal')
        self.assertIsInstance(d['para'], DecimalParam)
        d = parse_fields('para: Dimmension')
        self.assertIsInstance(d['para'], DimmensionParam)
        d = parse_fields('para: Text')
        self.assertIsInstance(d['para'], TextParam)
        d = parse_fields('para: Bool')
        self.assertIsInstance(d['para'], BoolParam)
        d = parse_fields('para: File', file_support=True)
        self.assertIsInstance(d['para'], FileParam)
        d = parse_fields('para: Image', file_support=True)
        self.assertIsInstance(d['para'], ImageParam)
 
    def test_valid_names(self):
        
        parse_fields("the_name: Bool")

        # Can't start with number or underscore
        with self.assertRaises(ParseException):
            parse_fields("1_name: Bool")
        with self.assertRaises(ParseException):
            parse_fields("_name: Bool")

        # Only lowercase allowed
        with self.assertRaises(ParseException):
            parse_fields("The_name: Bool")
        
        # spaces not allowed
        with self.assertRaises(ParseException):
            parse_fields("the name: Bool")

        # Other symbols not allowed
        for s in [".-,;{}[]!=?¿|@·$%&/()*<>'¡"]:
            with self.assertRaises(ParseException):
                parse_fields("name_{}:Bool".format(s))
            with self.assertRaises(ParseException):
                parse_fields("{}:Bool".format(s))

        # Test min and max lengths
        parse_fields("a: Bool")
        parse_fields("{}: Bool".format("a"*settings.PARAM_NAME_MAX_LENGTH))
        with self.assertRaises(ParseException):
            parse_fields(": Bool")
        with self.assertRaises(ParseException):
            parse_fields("{}: Bool".format("a"*(settings.PARAM_NAME_MAX_LENGTH+1)))

    def test_string_parsing(self):
        """Test string quotes format"""
        # Only double quotes allowed for strings
        parse_fields('name:Text-> default:"name"')
        with self.assertRaises(ParseException):
            parse_fields("name:Text-> default:'name'")
      
        # Test string escape character
        p=parse_fields('''name:Text-> default:"name \\"string\\""''')
        self.assertEqual(p['name'].default, 'name "string"')
    
        p=parse_fields('''name:Text-> default:"asdf\\n123\\""''')
        self.assertEqual(p['name'].default, 'asdf\n123"')

        original = TextParam(default='asdf\\\nasd\n"')
        parse = parse_fields('name:'+original.to_str())
        self.assertEqual(parse['name'].default, original.default)

        # Parse string with spaces inside
        p = parse_fields('name: Text-> default:" the default string  "')
        self.assertEqual(p['name'].default, ' the default string  ')

        # Length Limit
        p = parse_fields('name: Text-> default:"{}"'\
                .format("a"*settings.PARAM_TEXT_MAX_LENGTH))

        with self.assertRaises(ParseBaseException):
            parse_fields('name: Text-> default:"{}"'\
                .format("a"*(settings.PARAM_TEXT_MAX_LENGTH+1)))

    def test_boolean_parsing(self):
        """Test wich boolean strings are accepted"""
        # Control group
        p = parse_fields('enable:Bool->default:True')
        self.assertIsInstance(p['enable'].default, bool)
        self.assertEqual(p['enable'].default, True)
        p = parse_fields('enable:Bool->default:False')
        self.assertIsInstance(p['enable'].default, bool)
        self.assertEqual(p['enable'].default, False)

        # Invalid boolean values
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:false')
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:true')
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:f')
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:t')
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:#t')
        with self.assertRaises(ParseException):
            parse_fields('enable:Bool->default:#f')
        with self.assertRaises(ValueError):
            parse_fields('enable:Bool->default:1')
        with self.assertRaises(ValueError):
            parse_fields('enable:Bool->default:0')
        with self.assertRaises(ValueError):
            parse_fields('enable:Bool->default:"True"')
        with self.assertRaises(ValueError):
            parse_fields('enable:Bool->default:"False"')
        with self.assertRaises(ValueError):
            parse_fields('enable:Bool->default:33.5')

    def test_integer_parsing(self):
        """Test valid integer values"""
        # Control group
        p = parse_fields('holes: Integer->default:0')
        self.assertEqual(p['holes'].default, 0)

        p = parse_fields('holes: Integer->default:-0')
        self.assertEqual(p['holes'].default, 0)

        p = parse_fields('holes: Integer->default:-0000001')
        self.assertEqual(p['holes'].default, -1)

        p = parse_fields('holes: Integer->default:2')
        self.assertEqual(p['holes'].default, 2)
        
        p = parse_fields('holes: Integer->default:-1')
        self.assertEqual(p['holes'].default, -1)

        # max/min limits
        p = parse_fields('holes: Integer->default:{}'.format(settings.PARAM_INT_MAX))
        self.assertEqual(p['holes'].default, settings.PARAM_INT_MAX)

        p = parse_fields('holes: Integer->default:{}'.format(settings.PARAM_INT_MIN))
        self.assertEqual(p['holes'].default, settings.PARAM_INT_MIN)

        with self.assertRaises(ParseBaseException):
            parse_fields('holes: Integer->default:{}'.format(settings.PARAM_INT_MAX+1))
        
        with self.assertRaises(ParseBaseException):
            parse_fields('holes: Integer->default:{}'.format(settings.PARAM_INT_MIN-1))
       
        # Try overflow integer
        long_long_int = "9"+"9"*10000
        with self.assertRaises(ParseBaseException):
            parse_fields('holes: Integer->default:{}'.format(long_long_int))
    
    def test_decimal_parsing(self):
        """Test valid decimal values"""
        # Control group
        p = parse_fields('width: Decimal->default:0.0')
        self.assertEqual(p['width'].default, Decimal('0.0'))
        self.assertEqual(p['width'].default, 0)

        p = parse_fields('width: Decimal->default:-0.0')
        self.assertEqual(p['width'].default, Decimal('0.0'))
        self.assertEqual(p['width'].default, 0)
 
        p = parse_fields('width: Decimal->default:-0000000001.0')
        self.assertEqual(p['width'].default, Decimal('-1.0'))
        self.assertEqual(p['width'].default, -1)

        # Not decimal
        with self.assertRaises(Exception):
            parse_fields('width: Decimal->default:33,4')
        
        with self.assertRaises(Exception):
            parse_fields('width: Decimal->default:33e2')

        with self.assertRaises(Exception):
            parse_fields('width: Decimal->default:33')
        
        # max/min limits
        p = parse_fields('width: Decimal->default:{}'.format(settings.PARAM_DECIMAL_MAX))
        self.assertEqual(p['width'].default, settings.PARAM_DECIMAL_MAX)

        p = parse_fields('width: Decimal->default:{}'.format(settings.PARAM_DECIMAL_MIN))
        self.assertEqual(p['width'].default, settings.PARAM_DECIMAL_MIN)

        with self.assertRaises(ParseBaseException):
            parse_fields('width: Decimal->default:{}'.format(settings.PARAM_DECIMAL_MAX+1))
        
        with self.assertRaises(ParseBaseException):
            parse_fields('width: Decimal->default:{}'.format(settings.PARAM_DECIMAL_MIN-1))
     
        # max_digits and max_decimals
        p = parse_fields('width: Decimal->max_digits: 4 default:999.9')
        with self.assertRaises(Exception):
            p = parse_fields('width: Decimal->max_digits: 4 default:9999.9')

        p = parse_fields('width: Decimal->max_decimals: 2 default:999.99')
        with self.assertRaises(Exception):
            p = parse_fields('width: Decimal->max_decimals: 1 default:9.999')

        # Try overflow decimal
        long_long_decimal = "9"*10000+'.'+"9"*10000
        with self.assertRaises(ParseBaseException):
            parse_fields('width: Decimal-> default:{}'.format(long_long_decimal))

    def test_empty_choices_list(self):
        """Choices list must contain at least one element"""
        parse_fields("name:Integer-> choices:[1]")
        with self.assertRaises(ParseException):
            parse_fields("name:Integer-> choices:[]") 

    def test_errors_second_line(self):
        """Test parse errors"""
        with self.assertRaises(ParseException):
            parse_fields("number:Integer VALID:Bool")
        with self.assertRaises(ParseException):
            parse_fields("number:Integer-> default:12 hidden:Bool")
        with self.assertRaises(ParseException):
            parse_fields("number:Integer a:Bool hidden:33")
        with self.assertRaises(ParseException):
            parse_fields("number:Integer a:Bool 2:DecimalParam")
    
    def test_allowed_properties(self):
    
        # Test valid properties with correct parameter and value type.
        parse_fields('number:Integer->max:12 min:1 default:5 required:True hidden:True')
        parse_fields('number:Integer->even:True odd:True required:False hidden:False')
        parse_fields('number:Integer->default:33 choices:[22, 33, 44] required:False hidden:True')
        parse_fields('number:Text->max_length:44 min_length:1 required:False')
        parse_fields('activate:Bool->default:False hidden:False required:True')
        parse_fields('name:Text->help_text:"adfasd" label:"text input" required:False')
        parse_fields('length:Decimal->max:9999.9 min:9.99 default:100.0 max_decimals:2 max_digits:10 required:True default:44.9')

        # Test properties case sensitive.
        with self.assertRaises(ParseException):
            parse_fields("number:Integer-> mAx:12")
        with self.assertRaises(ParseException):
            parse_fields("input:Text-> max_length:14 Min_length:2")

        # Test properties not supported by parameter
        with self.assertRaises(ValueError):
            parse_fields("number:Integer-> max_length:12")
        with self.assertRaises(ValueError):
            parse_fields("number:Integer-> min_length:12")
        with self.assertRaises(ValueError):
            parse_fields("number:Integer-> max_digits:2")
        with self.assertRaises(ValueError):
            parse_fields("number:Integer-> max_decimals: 2")
       
        with self.assertRaises(ValueError):
            parse_fields("number:Decimal-> odd:True")
        with self.assertRaises(ValueError):
            parse_fields("number:Decimal-> even:True")
        with self.assertRaises(ValueError):
            parse_fields("number:Decimal-> max_length:12")
        with self.assertRaises(ValueError):
            parse_fields("number:Decimal-> min_length:12")
       
        with self.assertRaises(ValueError):
            parse_fields("number:Dimmension-> odd:True")
        with self.assertRaises(ValueError):
            parse_fields("number:Dimmension-> even:True")
        with self.assertRaises(ValueError):
            parse_fields("number:Dimmension-> max_length:12")
        with self.assertRaises(ValueError):
            parse_fields("number:Dimmension-> min_length:12")

        with self.assertRaises(ValueError):
            parse_fields("comment:Text-> odd:True")
        with self.assertRaises(ValueError):
            parse_fields("comment:Text-> even:True")
        with self.assertRaises(ValueError):
            parse_fields("comment:Text-> min:2")
        with self.assertRaises(ValueError):
            parse_fields("comment:Text-> max:5")
        with self.assertRaises(ValueError):
            parse_fields("number:Text-> max_digits:2")
        with self.assertRaises(ValueError):
            parse_fields("number:Text-> max_decimals:2")

        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> odd:True")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> even:True")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> min:1")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> max:2")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> min_length:1")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> max_length:3")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> max_digits:2")
        with self.assertRaises(ValueError):
            parse_fields("activate:Bool-> max_decimals:2")
   
        # Test invalid properties
        with self.assertRaises(ParseException):
            parse_fields("activate:Bool-> purse:3")
        with self.assertRaises(ParseException):
            parse_fields("number:Decimal-> car:3")

        # Test no properties are required
        parse_fields("activate:Bool")

    def test_properties_initialized(self):
        """Test properties are passed to param __init__ and initialized"""
        p = parse_fields('number:Integer->max:12 min:1 default:5 hidden:True')
        self.assertEqual(p['number'].max, 12)
        self.assertEqual(p['number'].min, 1)
        self.assertEqual(p['number'].default, 5)
        self.assertEqual(p['number'].hidden, True)

        p = parse_fields('number:Integer->even:True odd:True required:False')
        self.assertEqual(p['number'].even, True)
        self.assertEqual(p['number'].odd, True)
        self.assertEqual(p['number'].required, False)

        p = parse_fields('number:Integer->choices:[3, 4, 5, 6]')
        self.assertEqual(p['number'].choices[0], 3)
        self.assertEqual(p['number'].choices[1], 4)
        self.assertEqual(p['number'].choices[2], 5)
        self.assertEqual(p['number'].choices[3], 6)

        p = parse_fields('name:Text-> min_length:1 max_length:4')
        self.assertEqual(p['name'].min_length, 1)
        self.assertEqual(p['name'].max_length, 4)

        p = parse_fields('name:Text-> default:"324"')
        self.assertEqual(p['name'].default, '324')

        p = parse_fields('active:Bool-> label:"the real" help_text:"helpy"')
        self.assertEqual(p['active'].label, "the real")
        self.assertEqual(p['active'].help_text, "helpy")

        p = parse_fields('width:Decimal-> required: True max_digits: 10 max_decimals: 3 min:99.93')
        self.assertEqual(p['width'].max_digits, 10)
        self.assertEqual(p['width'].max_decimals, 3)
        self.assertEqual(p['width'].required, True)
        self.assertEqual(p['width'].min, Decimal('99.93'))

        p = parse_fields('width:Dimmension-> default:12.1 hidden:True')
        self.assertEqual(p['width'].hidden, True)
        self.assertEqual(p['width'].default, Decimal('12.1'))

        p = parse_fields('custom_file:File-> required:False', file_support=True)
        self.assertEqual(p['custom_file'].required, False)

    def test_properties_defaults(self):
        """Test properties default values"""
        p = parse_fields('par:Bool')
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].default, None)
        self.assertEqual(p['par'].hidden, False)
        self.assertEqual(p['par'].required, True)

        p = parse_fields('par:Text')
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].default, None)
        self.assertEqual(p['par'].choices, None)
        self.assertEqual(p['par'].max_length, settings.PARAM_TEXT_MAX_LENGTH)
        self.assertEqual(p['par'].min_length, 0)
        self.assertEqual(p['par'].hidden, False)
        self.assertEqual(p['par'].required, True)

        p = parse_fields('par:Integer')
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].default, None)
        self.assertEqual(p['par'].choices, None)
        self.assertEqual(p['par'].max, settings.PARAM_INT_MAX)
        self.assertEqual(p['par'].min, settings.PARAM_INT_MIN)
        self.assertEqual(p['par'].even, False)
        self.assertEqual(p['par'].odd, False) 
        self.assertEqual(p['par'].hidden, False)
        self.assertEqual(p['par'].required, True)

        p = parse_fields('par:Decimal')
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].default, None)
        self.assertEqual(p['par'].choices, None)
        self.assertEqual(p['par'].max, settings.PARAM_DECIMAL_MAX)
        self.assertEqual(p['par'].min, settings.PARAM_DECIMAL_MIN)
        self.assertEqual(p['par'].max_digits, settings.PARAM_DECIMAL_MAX_DIGITS)
        self.assertEqual(p['par'].max_decimals, settings.PARAM_DECIMAL_MAX_DECIMALS)
        self.assertEqual(p['par'].hidden, False)
        self.assertEqual(p['par'].required, True)

        p = parse_fields('par:Dimmension')
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].default, None)
        self.assertEqual(p['par'].choices, None)
        self.assertEqual(p['par'].max, settings.PARAM_DIMMENSION_MAX)
        self.assertEqual(p['par'].min, Decimal('0.0'))
        self.assertEqual(p['par'].max_digits, settings.PARAM_DIMMENSION_MAX_DIGITS)
        self.assertEqual(p['par'].max_decimals, settings.PARAM_DIMMENSION_MAX_DECIMALS)
        self.assertEqual(p['par'].hidden, False)
        self.assertEqual(p['par'].required, True)
        
        p = parse_fields('par:File', file_support=True)
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].required, True)

        p = parse_fields('par:Image', file_support=True)
        self.assertEqual(p['par'].label, '')
        self.assertEqual(p['par'].help_text, '')
        self.assertEqual(p['par'].required, True)


    def test_param_limits(self):
        # Test max name length
        p = parse_fields('{}: Bool'.format("a"*settings.PARAM_NAME_MAX_LENGTH))

        with self.assertRaises(ParseException):
            p = parse_fields('{}: Bool'.format("a"*settings.PARAM_NAME_MAX_LENGTH+"b"))
