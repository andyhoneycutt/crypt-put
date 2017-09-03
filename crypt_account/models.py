from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from fernet_fields import EncryptedTextField
from cryptography.fernet import Fernet
from rest_framework.authtoken.models import Token
import random
import string
import time


def create_secret_key():
    return ''.join([
        random.SystemRandom().choice("{}{}{}".format(
            string.ascii_letters, string.digits, string.punctuation
        )) for i in range(50)
    ])


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = EncryptedTextField(default=create_secret_key())
    salt = EncryptedTextField(max_length=255, default=create_secret_key())


class Key(models.Model):
    key = EncryptedTextField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        account = Account.objects.create(user=instance)
        for i in range(0,10):
            secret = Fernet.generate_key()
            key = Key(account=account, key=secret)
            key.save()


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
