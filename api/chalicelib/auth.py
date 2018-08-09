"""Functionality related to the OAuth2 flow and storing credentials.

Credentials are persisted to Google Cloud Datastore. An AES cypher is used to
encrypt user information passed through the state parameter.
"""

import base64
import json
import logging
import os

import requests
from cryptography.fernet import Fernet
from google.oauth2 import credentials
from google_auth_oauthlib import flow

from . import models, utils

Credentials = credentials.Credentials

# Scopes required to access the People API.
PEOPLE_API_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/plus.me',
    'https://www.googleapis.com/auth/calendar.readonly'
]

# Get client secret JSON from environment (populated from SSM)
get_client_secret = lambda: json.loads(
    os.environ.get('google_auth_client_secret'))
get_cipher_key = lambda: os.environ.get('oauth_cipher_key').encode('utf-8')


class OAuth2CallbackCipher(object):
    """Handles encryption and decryption of state parameters."""

    @classmethod
    def get_cipher(cls):
        key = get_cipher_key()
        return Fernet(key)

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


def get_authorization_url(event: dict, request):
    """Gets the authorization URL to redirect the user to.

    Args:
        event (dict): The parsed Event object of the event that requires
                      authorization to respond to.

    Returns:
        str: The authorization URL to direct the user to.
    """
    oauth2_callback_args = OAuth2CallbackCipher.encrypt({
        'user_name': event['user']['name'],
        'space_name': event['space']['name'],
        'thread_name': event['message']['thread']['name'],
        'redirect_url': event['configCompleteRedirectUrl'],
    })
    callback_url = utils.get_base_url(request, '/auth/callback')
    oauth2_flow = flow.Flow.from_client_config(
        get_client_secret(),
        scopes=PEOPLE_API_SCOPES,
        redirect_uri=callback_url)
    oauth2_url, _ = oauth2_flow.authorization_url(
        login_hint=event['user']['email'],
        access_type='offline',
        include_granted_scopes='true',
        state=oauth2_callback_args)
    return oauth2_url


def logout(user_name: str):
    """Logs out the user, removing their stored credentials and revoking the
    grant

    Args:
        user_name (str): The identifier of the user.
    """
    try:
        logging.info('Logging out user %s', user_name)
        user = models.User.get(user_name)
        user.delete()
        return True
    except models.User.DoesNotExist:
        logging.info('Ignoring logout request for user %s', user_name)
        return False


def on_oauth2_callback(request):
    """Handles the OAuth callback."""
    state = request.query_params.get('state')
    oauth2_callback_args = OAuth2CallbackCipher.decrypt(state)
    user_name, redirect_url = (
        oauth2_callback_args['user_name'],
        oauth2_callback_args['redirect_url'])
    callback_url = utils.get_base_url(request, '/auth/callback')
    oauth2_flow = flow.Flow.from_client_config(
        get_client_secret(),
        scopes=PEOPLE_API_SCOPES,
        redirect_uri=callback_url,
        state=state
    )
    oauth2_flow.fetch_token(authorization_response=utils.get_current_url(request, params=True))
    logging.warning(oauth2_flow.credentials.id_token)
    user = models.User(user_name)
    user.put_credentials(oauth2_flow.credentials)
    user.populate_from_profile()
    user.save()
    logging.info(
        'Storing credentials for user %s and redirecting to %s',
        user_name,
        redirect_url)
    requests.get(redirect_url)  # complete Chat flow
    return user # redirect after callback completes
