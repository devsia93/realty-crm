from django.db.models import DecimalField

from app.settings import MAX_DIGITS_DB, DECIMAL_PLACES_DB


class CustomDecimalField(DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = kwargs.pop('max_digits', MAX_DIGITS_DB)
        kwargs['decimal_places'] = kwargs.pop('decimal_places', DECIMAL_PLACES_DB)
        kwargs['default'] = kwargs.pop('default', 0)
        super().__init__(*args, **kwargs)
