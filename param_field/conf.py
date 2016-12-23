from django.conf import settings as django_settings
from django.conf import BaseSettings
from decimal import Decimal



class AppSettings(BaseSettings):

    def __getattribute__(self, attr):
        if attr == attr.upper():
            try:
                return getattr(django_settings, attr)
            except AttributeError:
                pass
        
        return super(AppSettings, self).__getattribute__(attr)



class Settings(AppSettings):

    # This are the absolute limits for all fields
    PARAM_LABEL_MAX_LENGTH = 40
    PARAM_HELP_TEXT_MAX_LENGTH = 200
    PARAM_NAME_MAX_LENGTH = 30

    # Itegers
    PARAM_INT_MAX =  2147483647
    PARAM_INT_MIN = -2147483648

    # Decimal
    PARAM_DECIMAL_MAX = Decimal("9999999999999999.9999") 
    PARAM_DECIMAL_MIN = Decimal("-9999999999999999.9999")
    PARAM_DECIMAL_MAX_DIGITS = 20
    PARAM_DECIMAL_MAX_DECIMALS = 4

    # Dimmension
    PARAM_DIMMENSION_MAX = Decimal("99999999.9999")
    PARAM_DIMMENSION_MIN = Decimal("0.0")
    PARAM_DIMMENSION_MAX_DIGITS = 12
    PARAM_DIMMENSION_MAX_DECIMALS = 4

    # Text/TextArea
    PARAM_TEXT_MAX_LENGTH = 300

    # Max_length used by ParamField when it isn't supplied
    PARAM_FIELD_MAX_LENGTH = 3000


settings = Settings()
