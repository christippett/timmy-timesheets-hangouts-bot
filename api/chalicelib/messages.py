import os
import json
from random import randint
from enum import Enum

import google_auth_httplib2
from google.oauth2 import service_account
from apiclient import discovery

from hangouts_helper.message import (Message, Card, CardHeader, Section,
    Image, KeyValue, ButtonList, TextButton, ImageButton, TextParagraph,
    ImageStyle, Icon)

from . import utils


INTERACTIVE_TEXT_BUTTON_ACTION = "doTextButtonAction"
INTERACTIVE_IMAGE_BUTTON_ACTION = "doImageButtonAction"
COPY_TIMESHEET_ACTION = 'COPY_TIMESHEET'
INTERACTIVE_BUTTON_PARAMETER_KEY = "param_key"
BOT_HEADER = 'Card Bot Python'


class ActionMethod(Enum):
    COPY_TIMESHEET = 'COPY_TIMESHEET'
    SHOW_THIS_WEEKS_TIMESHEET = 'SHOW_THIS_WEEKS_TIMESHEET'
    SHOW_LAST_WEEKS_TIMESHEET = 'SHOW_LAST_WEEKS_TIMESHEET'
    PROPOSE_TIMESHEET = 'PROPOSE_TIMESHEET'
    LOGIN = 'LOGIN'
    HELP = 'HELP'


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
    credentials = service_account.Credentials.from_service_account_info(creds, scopes=scopes)
    http = google_auth_httplib2.AuthorizedHttp(credentials)
    chat = discovery.build('chat', 'v1', http=http)
    chat.spaces().messages().create(
        parent=space_name,
        body=message).execute()


def create_action_card():
    this_week_start, this_week_end = utils.get_week_dates(0)
    last_week_start, last_week_end = utils.get_week_dates(-1)
    message = Message()
    message.add_card(
        Card(
            CardHeader(
                title="Timmy's Action Menu",
                subtitle="Top tips for Timmy Timesheets",
                image_url='https://timesheets.servian.fun/static/img/timmy.2fafd88.png',
                image_style=ImageStyle.AVATAR),
            Section(
                ButtonList(
                    TextButton(text="LOGIN").add_action(ActionMethod.LOGIN)),
                TextParagraph("Login and configure integration with TimePro")),
            Section(
                ButtonList(
                    TextButton(text="VIEW LAST WEEK'S TIMESHEET").add_action(
                        action_method=ActionMethod.SHOW_LAST_WEEKS_TIMESHEET,
                        parameters={'start_date': str(this_week_start), 'end_date': str(this_week_end)})),
                TextParagraph("Show last week's timesheet")),
            Section(
                ButtonList(
                    TextButton(text="VIEW THIS WEEK'S TIMESHEET").add_action(
                        action_method=ActionMethod.SHOW_THIS_WEEKS_TIMESHEET,
                        parameters={'start_date': str(last_week_start), 'end_date': str(last_week_end)})),
                TextParagraph("Show this week's timesheet")),
            Section(
                ButtonList(
                    TextButton(text="PROPOSE THIS WEEK'S TIMESHEET").add_action(
                        action_method=ActionMethod.PROPOSE_TIMESHEET,
                        parameters={'start_date': str(this_week_start), 'end_date': str(this_week_end)})),
                TextParagraph(
                    "Show Timmy's Best Guess™ at this week's timesheet. "
                    "You also have the option to make it real by updating your timesheet "
                    "right from this here chat. Rock on 🤘")),
            Section(
                TextParagraph('Bring up this menu anytime by typing <b>help</b>')
            )
    ))
    return message.output()


def create_reminder_meme():
    random_integer = randint(0, 4) + 1
    meme_url = f'https://timesheets.servian.fun/images/{random_integer}.jpg'
    message = Message()
    message.add_card(Card(Section(Image(image_url=meme_url))))
    return message.output()


def create_timesheet_success_card():
    message = Message()
    message.add_card(
        Card(
            Section(
                TextParagraph('Timesheet updated sucessfully 🎉'),
                ButtonList(
                    TextButton(text="VIEW ON TIMESHEETS.COM.AU").add_link('https://timesheets.com.au/login.asp')))))
    return message.output()


def create_card_response(text, show_menu_button=False, button_label="BACK"):
    message = Message()
    card = Card(Section(TextParagraph(text)))
    if show_menu_button:
        card.add_section(
            Section(ButtonList(TextButton(button_label).add_action(ActionMethod.HELP))))
    message.add_card(card)
    return message.output()


def create_timesheet_card(date_entries, user, title='Timesheet Summary', show_buttons=False):
    start_date = min(date_entries.keys())
    end_date = max(date_entries.keys())
    start_date_label = start_date.strftime('%d-%b-%Y')
    end_date_label = end_date.strftime('%d-%b-%Y')

    message = Message()
    card = Card(CardHeader(
        title=title,
        subtitle=f'{start_date_label} - {end_date_label}',
        image_url=user.picture,
        image_style=ImageStyle.AVATAR))

    # Loop through timesheet and construct widget_list
    widget_list = list()
    for date, entries in date_entries.items():
        date_label = date.strftime('%A, %d %B')
        widget_list.append(TextParagraph(f'<b>{date_label}</b>'))
        if not entries:
            widget_list.append(KeyValue(top_label='Incomplete', content='0.0', icon=Icon.CLOCK))
        for entry in entries:
            widget_list.append(KeyValue(
                top_label=entry.get('customer_description'),
                content=str(entry.get('hours')),
                bottom_label=entry.get('project_description'),
                icon=Icon.CLOCK))
    timesheet_section = Section(*widget_list)
    card.add_section(timesheet_section)

    if show_buttons:
        action_parameters = {
            'start_date': str(start_date),
            'end_date': str(end_date)}
        button_section = Section(
            ButtonList(
                TextButton('SAVE TIMESHEET').add_action(
                    action_method=ActionMethod.COPY_TIMESHEET,
                    parameters=action_parameters)))
        card.add_section(button_section)
    message.add_card(card)
    return message.output()
