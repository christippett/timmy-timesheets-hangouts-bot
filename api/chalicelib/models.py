from datetime import datetime

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute
from google.oauth2 import credentials


Credentials = credentials.Credentials


class Space(Model):
    class Meta:
        table_name = 'team2-space'
        region = 'ap-southeast-2'
    name = UnicodeAttribute(hash_key=True)
    type = UnicodeAttribute(null=False)


class User(Model):
    class Meta:
        table_name = 'team2-user'
        region = 'ap-southeast-2'
    name = UnicodeAttribute(hash_key=True)
    credentials = JSONAttribute(null=False)
    updated_timestamp = UTCDateTimeAttribute(null=False)

    def get_credentials(self):
        return Credentials(**self.credentials)

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