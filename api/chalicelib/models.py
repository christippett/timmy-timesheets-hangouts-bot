from datetime import datetime

import google_auth_httplib2
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute
from google.oauth2 import credentials
from apiclient import discovery


Credentials = credentials.Credentials

_DEFAULT_AWS_REGION = 'ap-southeast-2'


class Space(Model):
    class Meta:
        table_name = 'team2-space'
        region = _DEFAULT_AWS_REGION
    name = UnicodeAttribute(hash_key=True)  # event['space']['name']
    type = UnicodeAttribute(null=False)


class UserRegister(Model):
    class Meta:
        table_name = 'team2-user-register'
        region = _DEFAULT_AWS_REGION


class User(Model):
    class Meta:
        table_name = 'team2-user'
        region = _DEFAULT_AWS_REGION
    name = UnicodeAttribute(hash_key=True)  # event['user']['name']
    credentials = JSONAttribute(null=False)
    display_name = UnicodeAttribute(null=True)
    given_name = UnicodeAttribute(null=True)
    family_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    updated_timestamp = UTCDateTimeAttribute(null=False)

    def get_credentials(self):
        return Credentials(**self.credentials)

    def get_profile(self):
        creds = self.get_credentials()
        http = google_auth_httplib2.AuthorizedHttp(creds)
        people_api = discovery.build('people', 'v1', http=http)
        try:
            person = people_api.people().get(
                resourceName='people/me',
                personFields=','.join([
                    'names',
                    'addresses',
                    'emailAddresses',
                    'phoneNumbers',
                    'photos',
                ])).execute()
            return person
        except Exception as e:
            return None

    def populate_from_profile(self):
        person = self.get_profile()
        if person:
            names = names = person.get('names', [])
            primary_name = [n for n in names if n['metadata'].get('primary', False)]
            if primary_name:
                primary_name = primary_name[0]
                self.display_name = primary_name.get('displayName')
                self.given_name = primary_name.get('givenName')
                self.family_name = primary_name.get('familyName')
            email_addresses = person.get('emailAddresses', [])
            primary_email = [e for e in email_addresses if e['metadata'].get('primary', False)]
            if primary_email:
                primary_email = primary_email[0]
                self.email = primary_email.get('value')

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