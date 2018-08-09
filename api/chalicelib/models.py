from datetime import datetime

import google_auth_httplib2
import requests
from apiclient import discovery
from google.oauth2 import credentials
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute, BinaryAttribute
from pynamodb.models import Model
from timepro_timesheet.api import TimesheetAPI

from . import auth

Credentials = credentials.Credentials

_DEFAULT_AWS_REGION = 'ap-southeast-2'


class Space(Model):
    class Meta:
        table_name = 'team2-space'
        region = _DEFAULT_AWS_REGION

    name = UnicodeAttribute(hash_key=True)  # event['space']['name']
    username = UnicodeAttribute(null=False)  # event['user']['name']
    type = UnicodeAttribute(null=False)

    @classmethod
    def get_from_email(cls, email: str):
        # extract first member of scan, assuming first entry
        user_results = list(User.scan(filter_condition=(User.email == email)))
        if user_results:
            user = user_results[0]
        else:
            raise cls.DoesNotExist
        space_results = list(cls.scan(filter_condition=(cls.username == user.username)))
        if space_results:
            return space_results[0]
        raise cls.DoesNotExist

    @classmethod
    def get_from_username(cls, username: str):
        space_results = list(cls.scan(filter_condition=(cls.username == username)))
        if space_results:
            return space_results[0]
        raise cls.DoesNotExist


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
        return auth.OAuth2CallbackCipher.decrypt(self.timepro_password_encrypted, True)

    @timepro_password.setter
    def timepro_password(self, value):
        self.timepro_password_encrypted = auth.OAuth2CallbackCipher.encrypt(args={}, pword=value)


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
    _api = None

    def get_api_and_login(self):
        if self._api is None:
            user_register = UserRegister.get(self.username)
            api = TimesheetAPI()
            api.login(customer_id=user_register.timepro_customer,
                      username=user_register.timepro_username,
                      password=user_register.timepro_password)
            self._api = api  # cache api
        return self._api

    def get_timesheet(self, start_date, end_date):
        api = self.get_api_and_login()
        return api.get_timesheet(start_date=start_date, end_date=end_date)

    def get_credentials(self):
        return Credentials(**self.credentials)

    def get_profile(self):
        creds = self.get_credentials()
        http = google_auth_httplib2.AuthorizedHttp(creds)
        oauth_api = discovery.build('oauth2', 'v2', http=http)
        try:
            user_info = oauth_api.userinfo().get().execute()
            return user_info
        except Exception as e:
            return None

    def populate_from_profile(self):
        profile = self.get_profile()
        if profile:
            self.email = profile.get('email')
            self.display_name = profile.get('display_name')
            self.given_name = profile.get('given_name')
            self.family_name = profile.get('family_name')
            self.picture = profile.get('picture')
            self.google_id = profile.get('id')

    def put_credentials(self, creds: Credentials) -> None:
        """Stores OAuth2 credentials for a user.

        Args:
            user_name (str): The identifier for the associated user.
            creds (Credentials): The OAuth2 credentials obtained for the user.
        """
        self.credentials = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
        }

    def save(self, **kwargs):
        self.updated_timestamp = datetime.now()
        return super().save(**kwargs)

    def delete(self, **kwargs):
        creds = self.get_credentials()
        requests.post(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token': creds.token},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return super().delete(**kwargs)


class Timesheet(Model):
    class Meta:
        table_name = 'team2-timesheets'
        region = _DEFAULT_AWS_REGION

    username = UnicodeAttribute(hash_key=True)
    date = UTCDateTimeAttribute(range_key=True)
    entries = JSONAttribute(null=False)
    email = UnicodeAttribute(null=True)
    updated_timestamp = UTCDateTimeAttribute(null=False)

    @classmethod
    def bulk_create_from_date_entries(cls, user, date_entries):
        for date, entries in date_entries.items():
            entry_data = {'entries': entries}
            ts = cls(user.username, date, entries=entry_data, email=user.email)
            ts.save()

    def save(self, **kwargs):
        self.updated_timestamp = datetime.now()
        return super().save(**kwargs)
