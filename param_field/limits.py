from decimal import Decimal

# This are the absolute limits for all fields

LABEL_MAX_LENGTH = 40
HELP_TEXT_MAX_LENGTH = 200

# Itegers
INT_MAX = 999999
INT_MIN = -999999

# Decimal/Dimmension 
DECIMAL_MAX = Decimal("999999999999.9999") 
DECIMAL_MIN = Decimal("-999999999999.9999")
DECIMAL_MAX_DIGITS = 20
DECIMAL_MAX_DECIMALS = 4

# Length
STRING_MAX_LENGTH = 300
