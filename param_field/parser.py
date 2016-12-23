from pyparsing import *
from decimal import Decimal
from collections import OrderedDict
from .params import *

FIELD_TO_PARAM = {
    'Bool': BoolParam,
    'Decimal': DecimalParam,
    'Dimmension': DimmensionParam,
    'Integer': IntegerParam,
    'Text': TextParam,
    'TextArea': TextAreaParam,
    'File': FileParam,
    'Image': ImageParam,
}


reserved_keywords = Keyword("Integer")|Keyword("Bool")|Keyword("Dimmension")\
        |Keyword("Decimal")|Keyword("Text")|Keyword("TextArea")|Keyword("File")\
        |Keyword("Image")|Keyword("default")|Keyword("min_length")|Keyword("max_length")\
        |Keyword("min")|Keyword("max")|Keyword("help_text")|Keyword("label")\
        |Keyword("hidden")|Keyword("odd")|Keyword("even")|Keyword("choices")\
        |Keyword("required")|Keyword("max_digits")|Keyword("max_decimals")

cvtInt = lambda t: int(t[0])
cvtDec = lambda t: Decimal(t[0])
cvtBool = lambda t: (True if t[0]=="True" else False)

def rangeCheck(minval=None, maxval=None):
    if minval is None and maxval is None:
        # this exception occurs not at parse time, but while defining the grammar
        raise ValueError("minval or maxval must be specified")

    def rangeCheckParseAction(string, loc, tokens):
        parsedval = tokens[0]
        if minval is not None:
            if maxval is not None:
                valid = minval <= parsedval <= maxval
            else:
                valid = minval <= parsedval
        else:
            if maxval is not None:
                valid = parsedval <= maxval

        if not valid:
            err = "value not in range ({},{})".format(minval, maxval)
            raise ParseFatalException(string, loc, err)

    return rangeCheckParseAction    

def lengthCheck(max_length=settings.PARAM_TEXT_MAX_LENGTH):

    def lengthCheckParseAction(string, loc, tokens):
        if len(tokens[0]) > max_length:
            err = "string exceeds maximum length".format(max_length)
            raise ParseFatalException(string, loc, err)

    return lengthCheckParseAction

def propToDict(tokens):
    """Convert field property list to dictionary"""
    prop_dict = OrderedDict()

    for token in tokens:
        prop_dict[token.property_name] = token.property_value

    return prop_dict

def lstToList(tokens):
    """Convert list of list of tokes to python list"""
    l = list()
    
    for token in tokens[0]:
        l.append(token)
    
    return [l]

def fieldToParam(token):
    name, field_type, props = token.field 
    return (name, FIELD_TO_PARAM[field_type](**props))


lowercase = "abcdefghijklmnopqrstuvwxyz"
lowercasenums = "abcdefghijklmnopqrstuvwxyz0123456789"
arithOp = Word("+-*/^", max=1)
lparen,rparen,lbrack,rbrack,lbrace,rbrace = map(Suppress,"()[]{}")
colon = Suppress(":")
comma = Suppress(",")
plusorminus = oneOf("+ -")
arrow = Suppress("->")
number = Word(nums)


# Define data primitives and limits
integer = Combine(Optional(plusorminus)+number)\
    .setName("integer").setParseAction(cvtInt)\
    .addParseAction(rangeCheck(settings.PARAM_INT_MIN, settings.PARAM_INT_MAX))
real = Combine(Optional(plusorminus)+number+"."+number)\
    .setName("real").setParseAction(cvtDec)\
    .addParseAction(rangeCheck(settings.PARAM_DECIMAL_MIN, settings.PARAM_DECIMAL_MAX))
string = QuotedString('"', escChar='\\')\
    .setName("string")\
    .addParseAction(lengthCheck())
boolean = oneOf("True False").setName("bool")\
    .setParseAction(cvtBool)
lst_elem = real | integer | string
lst = Group(lbrack+lst_elem+ZeroOrMore(comma+lst_elem)+Optional(comma)+rbrack)\
    .addParseAction(lstToList)



identifier = ~reserved_keywords+Word(lowercase, lowercasenums+"_", min=1, max=settings.PARAM_NAME_MAX_LENGTH)


key = oneOf("default min_length max_length min max help_text label hidden odd even choices required max_digits max_decimals")\
    .setResultsName("property_name")
value = (real | integer | boolean | string | lst).setResultsName("property_value")
field_property = Group(key + colon + value)



def create_parser(types="Integer Dimmension Decimal Bool Text TextArea"):
    """
    Arguments:
        types: Supported types string
    """ 
    field_type = oneOf(types)

    field = Group(identifier + colon + field_type +\
                Optional(arrow+OneOrMore(field_property))\
                    .setParseAction(propToDict)\
                    .setResultsName("property_dict"))\
            .setResultsName("field").setParseAction(fieldToParam)

    params = ZeroOrMore(field)

    return params



params = create_parser(
        types = "Integer Dimmension Decimal Bool Text TextArea")

params_file = create_parser(
        types = "Integer Dimmension Decimal Bool Text TextArea File Image")

params.enablePackrat()
params_file.enablePackrat()


def parse_fields(input_str, file_support=False):
    """
    Arguments:
        input_str (string): 
        file_support (bool): Enable support to file parameters
            File
            Image
    """ 
    if file_support:
        ast = params_file.parseString(input_str, parseAll=True)
    else:
        ast = params.parseString(input_str, parseAll=True)
    
    d = OrderedDict()
    for name, field in ast:
        d[name] = field
    return d



















