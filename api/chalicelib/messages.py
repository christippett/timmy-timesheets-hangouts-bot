import os
import json

from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery
from httplib2 import Http


INTERACTIVE_TEXT_BUTTON_ACTION = "doTextButtonAction"
INTERACTIVE_IMAGE_BUTTON_ACTION = "doImageButtonAction"
COPY_TIMESHEET_ACTION = 'COPY_TIMESHEET'
INTERACTIVE_BUTTON_PARAMETER_KEY = "param_key"
BOT_HEADER = 'Card Bot Python'


get_service_account = lambda: json.loads(
    os.environ.get('google_auth_service_account'))



def send_async_message(message, space_name, thread_id=None, creds=None):
    """Sends a response back to the Hangouts Chat room asynchronously.

    Args:
      response: the response payload
      spaceName: The URL of the Hangouts Chat room

    """
    if creds is None:
        creds = get_service_account()

    # The following two lines of code update the thread that raised the event.
    # Delete them if you want to send the message in a new thread.
    if thread_id is not None:
        message['thread'] = thread_id

    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        creds, scopes)
    http_auth = credentials.authorize(Http())

    chat = discovery.build('chat', 'v1', http=http_auth)
    chat.spaces().messages().create(
        parent=space_name,
        body=message).execute()


def create_timesheet_card(date_entries, user):
    response = dict()
    cards = list()
    widgets = list()

    # Create header
    start_date = min(date_entries.keys())
    end_date = max(date_entries.keys())
    start_date_label = start_date.strftime('%d-%b-%Y')
    end_date_label = end_date.strftime('%d-%b-%Y')
    header = {
        'header': {
            'title': 'Timesheet Summary',
            'subtitle': f'{start_date_label} - {end_date_label}',
            'imageUrl': user.picture,
            'imageStyle': 'AVATAR'
        }
    }
    cards.append(header)

    # Loop through timesheet and construct widgets
    for date, entries in date_entries.items():
        date_label = date.strftime('%A, %b %d')
        widgets.append({
            'textParagraph' : {
                'text': f'<b>{date_label}</b>'
            }
        })
        for entry in entries:
            widgets.append({
                'keyValue': {
                    'topLabel': entry.get('customer_description'),
                    'content': str(entry.get('hours')),
                    'bottomLabel': entry.get('project_description'),
                    'icon': 'CLOCK'
                }
            })
    cards.append({ 'sections': [{ 'widgets': widgets }]})

    button_widgets = list()
    button_widgets.append({
        'buttons': [
            {
                'textButton': {
                    'text': 'COPY TIMESHEET FORWARD',
                    'onClick': {
                        'action': {
                            'actionMethodName': COPY_TIMESHEET_ACTION,
                            'parameters': [{
                                'key': 'start_date',
                                'value': str(start_date)
                            },
                            {
                                'key': 'end_date',
                                'value': str(end_date)
                            }]
                        }
                    }
                }
            }
        ]
    })
    button_widgets.append({
        'buttons': [
            {
                'textButton': {
                    'text': 'VIEW TIMESHEET',
                    'onClick': {
                        'openLink': {
                            'url': 'https://timesheets.com.au',
                        }
                    }
                }
            }
        ]
    })
    cards.append({ 'sections': [{ 'widgets': button_widgets }]})

    response['cards'] = cards
    return response


def create_card_response(event_message):
    """Creates a card response based on the message sent in Hangouts Chat.

    See the reference for JSON keys and format for cards:
    https://developers.google.com/hangouts/chat/reference/message-formats/cards

    Args:
        eventMessage: the user's message to the bot

    """

    response = dict()
    cards = list()
    widgets = list()
    header = None

    words = event_message.lower().split()

    for word in words:

        if word == 'header':
            header = {
                'header': {
                    'title': BOT_HEADER,
                    'subtitle': 'Card header',
                    'imageUrl': 'https://goo.gl/5obRKj',
                    'imageStyle': 'IMAGE'
                }
            }

        elif word == 'textparagraph':
            widgets.append({
                'textParagraph' : {
                    'text': '<b>This</b> is a <i>text paragraph</i>.'
                }
            })

        elif word == 'keyvalue':
            widgets.append({
                'keyValue': {
                    'topLabel': 'KeyValue Widget',
                    'content': 'This is a KeyValue widget',
                    'bottomLabel': 'The bottom label',
                    'icon': 'STAR'
                }
            })

        elif word == 'interactivetextbutton':
            widgets.append({
                'buttons': [
                    {
                        'textButton': {
                            'text': 'INTERACTIVE BUTTON',
                            'onClick': {
                                'action': {
                                    'actionMethodName': INTERACTIVE_TEXT_BUTTON_ACTION,
                                    'parameters': [{
                                        'key': INTERACTIVE_BUTTON_PARAMETER_KEY,
                                        'value': event_message
                                    }]
                                }
                            }
                        }
                    }
                ]
            })

        elif word == 'interactiveimagebutton':
            widgets.append({
                'buttons': [
                    {
                        'imageButton': {
                            'icon': 'EVENT_SEAT',
                            'onClick': {
                                'action': {
                                    'actionMethodName': INTERACTIVE_IMAGE_BUTTON_ACTION,
                                    'parameters': [{
                                        'key': INTERACTIVE_BUTTON_PARAMETER_KEY,
                                        'value': event_message
                                    }]
                                }
                            }
                        }
                    }
                ]
            })

        elif word == 'textbutton':
            widgets.append({
                'buttons': [
                    {
                        'textButton': {
                            'text': 'TEXT BUTTON',
                            'onClick': {
                                'openLink': {
                                    'url': 'https://developers.google.com',
                                }
                            }
                        }
                    }
                ]
            })

        elif word == 'imagebutton':
            widgets.append({
                'buttons': [
                    {
                        'imageButton': {
                            'icon': 'EVENT_SEAT',
                            'onClick': {
                                'openLink': {
                                    'url': 'https://developers.google.com',
                                }
                            }
                        }
                    }
                ]
            })

        elif word == 'image':
            widgets.append({
                'image': {
                    'imageUrl': 'https://goo.gl/Bpa3Y5',
                    'onClick': {
                        'openLink': {
                            'url': 'https://developers.google.com'
                        }
                    }
                }
            })



    if header != None:
        cards.append(header)

    cards.append({ 'sections': [{ 'widgets': widgets }]})
    response['cards'] = cards

    return response


def respond_to_interactive_card_click(action_name, custom_params):
    """Creates a response for when the user clicks on an interactive card.

    See the guide for creating interactive cards
    https://developers.google.com/hangouts/chat/how-tos/cards-onclick

    Args:
        action_name: the name of the custom action defined in the original bot response
        custom_params: the parameters defined in the original bot response

    """
    message = 'You clicked {}'.format(
        'a text button' if action_name == INTERACTIVE_TEXT_BUTTON_ACTION
            else 'an image button')

    original_message = ""

    if custom_params[0]['key'] == INTERACTIVE_BUTTON_PARAMETER_KEY:
        original_message = custom_params[0]['value']
    else:
        original_message = '<i>Cannot determine original message</i>'

    # If you want to respond to the same room but with a new message,
    # change the following value to NEW_MESSAGE.
    action_response = 'UPDATE_MESSAGE'

    return {
        'actionResponse': {
            'type': action_response
        },
        'cards': [
            {
                'header': {
                    'title': BOT_HEADER,
                    'subtitle': 'Interactive card clicked',
                    'imageUrl': 'https://goo.gl/5obRKj',
                    'imageStyle': 'IMAGE'
                }
            },
            {
                'sections': [
                    {
                        'widgets': [
                            {
                                'textParagraph': {
                                    'text': message
                                }
                            },
                            {
                                'keyValue': {
                                    'topLabel': 'Original message',
                                    'content': original_message
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }