from django.test import TestCase, override_settings
from param_field.conf import settings


class TestConf(TestCase):

    
    @override_settings(PARAM_INT_MAX=3)
    def test_custom_config(self):
        """Test setting value overrides default values"""
        self.assertEqual(settings.PARAM_INT_MAX, 3)


    def test_default_config(self):
        """Test default options are used when not set in settings.py"""
        # This are the absolute limits for all fields
        self.assertTrue(settings.PARAM_LABEL_MAX_LENGTH>0)
        self.assertTrue(settings.PARAM_HELP_TEXT_MAX_LENGTH>0)
        self.assertTrue(settings.PARAM_NAME_MAX_LENGTH>0)

        # Itegers
        self.assertTrue(settings.PARAM_INT_MAX>0)
        self.assertTrue(settings.PARAM_INT_MIN<0)

        # Decimal
        self.assertTrue(settings.PARAM_DECIMAL_MAX>0)
        self.assertTrue(settings.PARAM_DECIMAL_MIN<0)
        self.assertTrue(settings.PARAM_DECIMAL_MAX_DIGITS>0)
        self.assertTrue(settings.PARAM_DECIMAL_MAX_DECIMALS>0)

        # Dimmension
        self.assertTrue(settings.PARAM_DIMMENSION_MAX>0)
        self.assertTrue(settings.PARAM_DIMMENSION_MIN==0)
        self.assertTrue(settings.PARAM_DIMMENSION_MAX_DIGITS>0)
        self.assertTrue(settings.PARAM_DIMMENSION_MAX_DECIMALS>0)

        # Strings
        self.assertTrue(settings.PARAM_TEXT_MAX_LENGTH>0)

        # Field's default max_length
        self.assertTrue(settings.PARAM_FIELD_MAX_LENGTH>0)
