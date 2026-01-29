from django.db import models

from core.crypto import decrypt, encrypt


class EncryptedCharField(models.CharField):
    def get_prep_value(self, value):
        if not value:
            return value
        return encrypt(value)

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        return decrypt(value)

    def to_python(self, value):
        if not value:
            return value
        if "$" in value:
            return decrypt(value)
        return value
