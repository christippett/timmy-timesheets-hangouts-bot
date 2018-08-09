import base64
import json
import os

import boto3
from cryptography.fernet import Fernet

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute, BinaryAttribute

_DEFAULT_AWS_REGION = 'ap-southeast-2'

get_cipher_key = lambda: os.environ.get('oauth_cipher_key', 'j7YMwzPCVphqNKJk4ZnialTsP0naZ18vhyQpL3iMz7o=').encode(
    'utf-8')


class OAuth2CallbackCipher(object):
    """Handles encryption and decryption of state parameters."""
    key = get_cipher_key()

    @classmethod
    def get_cipher(cls):
        return Fernet(cls.key)

    @classmethod
    def encrypt(cls, args: dict, pword: str = None) -> str:

        if not pword:
            # Produce JSON payload, padded to multiple of 16 bytes.
            str_to_encrypt = json.dumps(args)
        else:
            str_to_encrypt = pword

        str_to_encrypt = str_to_encrypt.ljust(-(-len(str_to_encrypt) // 16) * 16)
        return base64.b64encode(
            cls.get_cipher().encrypt(str_to_encrypt.encode('utf-8')))

    @classmethod
    def decrypt(cls, encrypted_args: str, pword: bool = False) -> dict:
        decrypted = cls.get_cipher().decrypt(
            base64.b64decode(encrypted_args)).rstrip().decode('utf-8')
        return decrypted if pword else json.loads(decrypted)


class UserRegister(Model):
    class Meta:
        table_name = 'team2-user-register'
        region = _DEFAULT_AWS_REGION

    username = UnicodeAttribute(hash_key=True)  # User email
    timepro_username = UnicodeAttribute(null=False)
    timepro_password_encrypted = BinaryAttribute(null=False)
    timepro_customer = UnicodeAttribute(null=False)

    @property
    def timepro_password(self):
        return OAuth2CallbackCipher.decrypt(self.timepro_password_encrypted, True)

    @timepro_password.setter
    def timepro_password(self, value):
        self.timepro_password_encrypted = OAuth2CallbackCipher.encrypt(args={}, pword=value)


def scan():
    sess = boto3.Session(region_name='ap-southeast-2', profile_name='team2servian')
    res = sess.resource('dynamodb')
    ureg = res.Table('team2-user-register')

    resp = ureg.scan()
    os.environ["AWS_PROFILE"] = "team2servian"

    for r in resp["Items"]:
        print(r)
        user_register = UserRegister(
            username=r["username"],
            timepro_username=r['timepro_username'],
            timepro_customer=r['timepro_customer'])
        user_register.timepro_password = r['timepro_password']
        user_register.save()

    for r in UserRegister.scan():
        print(r.timepro_password)


def new_table():
    sess = boto3.Session(region_name='ap-southeast-2', profile_name='team2servian')
    res = sess.resource('dynamodb')
    ureg = res.Table('team2-user-register-alt')

    resp = ureg.scan()

    old_table = res.Table('team2-user-register')

    for r in resp["Items"]:
        old_table.put_item(
            Item={
                'username': r["username"],
                'timepro_username': r["timepro_username"],
                'timepro_password_encrypted': r["timepro_password_encrypted"],
                "timepro_customer": r["timepro_customer"]

            }
        )





    # os.environ["AWS_PROFILE"] = "team2servian"
    # for r in UserRegister.scan():
    #     print(r.timepro_password)

if __name__ == "__main__":
    # scan()
    new_table()
