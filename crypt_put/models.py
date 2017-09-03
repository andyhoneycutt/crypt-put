from django.db import models
from crypt_account.models import *
from cryptography.fernet import MultiFernet, Fernet
import hashlib
from base64 import b64encode

def make_uid(salt, pepper, key):
    s = b64encode(salt)
    p = b64encode(pepper)
    k = b64encode(key)
    return hashlib.sha256(s + p + k).hexdigest()


class Record(models.Model):
    uid = models.CharField(max_length=255, primary_key=True)
    data = models.BinaryField()

    def save(self, *args, **kwargs):
        keys = kwargs.pop('keys')
        fkeys = [Fernet(key) for key in keys]
        encrypted_data = MultiFernet(fkeys).encrypt(self.data)
        self.data = encrypted_data
        return super(Record, self).save(*args, **kwargs)
