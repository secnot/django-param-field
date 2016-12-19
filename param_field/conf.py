from django.conf import settings as django_settings
from decimal import Decimal



class Settings(object):

    # This are the absolute limits for all fields
    LABEL_MAX_LENGTH = 40
    HELP_TEXT_MAX_LENGTH = 200

    # Itegers
    INT_MAX = 999999
    INT_MIN = -999999

    # Decimal
    DECIMAL_MAX = Decimal("999999999999.9999") 
    DECIMAL_MIN = Decimal("-999999999999.9999")
    DECIMAL_MAX_DIGITS = 20
    DECIMAL_MAX_DECIMALS = 4

    # Dimmension
    DIMMENSION_MAX = Decimal("99999999.9999")
    DIMMENSION_MIN = Decimal("0.0")
    DIMMENSION_MAX_DIGITS = 12
    DIMMENSION_MAX_DECIMALS = 4

    # Strings
    STRING_MAX_LENGTH = 300
    
    def __init__(self, *args, **kwargs):
        #TODO: Override defaults loading from settings.py
        pass


settings = Settings()
