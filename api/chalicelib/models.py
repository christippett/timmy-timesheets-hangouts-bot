from datetime import datetime

import google_auth_httplib2
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute, ListAttribute
from google.oauth2 import credentials
from apiclient import discovery


Credentials = credentials.Credentials

_DEFAULT_AWS_REGION = 'ap-southeast-2'


class Space(Model):
    class Meta:
        table_name = 'team2-space'
        region = _DEFAULT_AWS_REGION
    name = UnicodeAttribute(hash_key=True)  # event['space']['name']
    username = UnicodeAttribute(null=False)  # event['user']['name']
    type = UnicodeAttribute(null=False)


class UserRegister(Model):
    class Meta:
        table_name = 'team2-user-register'
        region = _DEFAULT_AWS_REGION
    username = UnicodeAttribute(hash_key=True)  # User email
    timepro_username = UnicodeAttribute(null=False)
    timepro_password = UnicodeAttribute(null=False)
    timepro_customer = UnicodeAttribute(null=False)


class User(Model):
    class Meta:
        table_name = 'team2-user'
        region = _DEFAULT_AWS_REGION
    username = UnicodeAttribute(hash_key=True)  # event['user']['name']
    credentials = JSONAttribute(null=False)
    display_name = UnicodeAttribute(null=True)
    given_name = UnicodeAttribute(null=True)
    family_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    picture = UnicodeAttribute(null=True)
    google_id = UnicodeAttribute(null=True)
    updated_timestamp = UTCDateTimeAttribute(null=False)


class Timesheet(Model):
    class Meta:
        table_name = 'team2-scrape'
        region = _DEFAULT_AWS_REGION
    username = UnicodeAttribute(hash_key=True)
    date = UTCDateTimeAttribute(range_key=True)
    entries = ListAttribute(null=False)
    updated_timestamp = UTCDateTimeAttribute(null=False)

    def save(self, **kwargs):
        self.updated_timestamp = datetime.now()
        return super().save(**kwargs)