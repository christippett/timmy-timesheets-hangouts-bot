import traceback
from enum import Enum
from random import randint

from datetime import timedelta
from dateutil.parser import parse as dateparser

from hangouts_helper.message import (Message, Card, CardHeader, Section,
    Image, KeyValue, ButtonList, TextButton, ImageButton, TextParagraph,
    ImageStyle, Icon, ResponseType)
from hangouts_helper.handler import HangoutsChatHandler, SpaceType, EventType
from hangouts_helper.api import HangoutsChatAPI

from . import models, utils, auth


class ActionMethod(Enum):
    COPY_TIMESHEET = 'COPY_TIMESHEET'
    SHOW_THIS_WEEKS_TIMESHEET = 'SHOW_THIS_WEEKS_TIMESHEET'
    SHOW_LAST_WEEKS_TIMESHEET = 'SHOW_LAST_WEEKS_TIMESHEET'
    PROPOSE_TIMESHEET = 'PROPOSE_TIMESHEET'
    LOGIN = 'LOGIN'
    HELP = 'HELP'
    REFRESH_TIMESHEET_DATA = 'REFRESH_TIMESHEET_DATA'


class TimmyBaseHandler(HangoutsChatHandler):
    ActionMethod = ActionMethod

    def __init__(self, parameters={}, service_account_info=None, *args, **kwargs):
        self.parameters = parameters
        self.chat = HangoutsChatAPI(service_account_info)
        super().__init__(*args, **kwargs)

    def handle_exception(self, e, **kwargs):
        event = kwargs.get('event')
        if self.debug and event:
            content = traceback.format_exc()
            space_name = event['space']['name']
            self.chat.create_message(
                message={'text': content},
                space_name=space_name)

    def handle_event_asynchronously(self, event):
        sqs_parameters = self.parameters.get('sqs_parameters', {})
        sqs_queue_process_id = sqs_parameters.get('sqs_queue_process_id')
        if sqs_queue_process_id:
            utils.sqs_send_message(queue_url=sqs_queue_process_id, message=event)

    def request_config(self, event):
        client_secret = self.parameters.get('google_auth_client_secret')
        callback_url = self.parameters.get('config_callback_url')
        state = {
            'user_name': event['user']['name'],
            'user_email': event['user']['email'],
            'space_name': event['space']['name'],
            'thread_name': event['message']['thread']['name'],
            'redirect_url': event['configCompleteRedirectUrl']
        }
        oauth2_url = auth.get_authorization_url(callback_url, state, client_secret)
        return Message.request_config(url=oauth2_url).output()

    def authenticate_user(self, username):
        try:
            user = models.User.get(username)
            models.UserRegister.get(username)
        except (models.User.DoesNotExist, models.UserRegister.DoesNotExist):
            return None
        return user


class TimmySyncHandler(TimmyBaseHandler):

    def handle_added_to_space(self, space_type, event):
        # Register new space in DB
        space = models.Space(
            hash_key=event['space']['name'],
            type=event['space']['type'],
            username=event['user']['name'])
        space.save()
        if space_type == SpaceType.DIRECT_MESSAGE:
            return Message(text='Hey, thanks for adding me 🎉! Type *help* to get started...').output()

    def handle_removed_from_space(self, event):
        try:
            models.Space.get(event['space']['name']).delete()
            models.User.get(event['user']['name']).delete()
            models.UserRegister.get(event['user']['name']).delete()
        except (models.Space.DoesNotExist, models.User.DoesNotExist):
            pass
        return

    def handle_message(self, message, event):
        message_text = message['text'].lower()
        user_name = event['user']['name']
        user = self.authenticate_user(user_name)
        if not user:
            return self.request_config(event)
        if message_text == 'help':
            return MessageTemplate.action_card().output()
        elif message_text in ['remind_everyone', 'remind_everyone_meme']:
            self.handle_event_asynchronously(event)
            return Message(text='Sending a reminder to everyone!').output()
        elif message_text == 'logout':
            user.delete()
            return Message(text="You've been logged out and your TimePro credentials deleted.").output()

    def handle_card_clicked(self, action_method, action_parameters, event):
        if action_method == self.ActionMethod.COPY_TIMESHEET:
            self.handle_event_asynchronously(event)
            msg = MessageTemplate.timesheet_updated_successfully().output()
            msg['actionResponse'] = {'type': 'UPDATE_MESSAGE'}
            return msg
        elif action_method == self.ActionMethod.HELP:
            msg = MessageTemplate.action_card().output()
            msg['actionResponse'] = {'type': 'UPDATE_MESSAGE'}
            return msg
        elif action_method == self.ActionMethod.SHOW_THIS_WEEKS_TIMESHEET:
            self.handle_event_asynchronously(event)
            return Message(
                text="I'm off to track down this week's timesheet... ⌛",
                response_type=ResponseType.UPDATE_MESSAGE).output()
        elif action_method == self.ActionMethod.SHOW_LAST_WEEKS_TIMESHEET:
            self.handle_event_asynchronously(event)
            return Message(
                text="I'm off to track down last week's timesheet... ⌛",
                response_type=ResponseType.UPDATE_MESSAGE).output()
        elif action_method == self.ActionMethod.PROPOSE_TIMESHEET:
            self.handle_event_asynchronously(event)
            return Message(
                text="Thinking cap is on! I'm off to divine this week's timesheet... ⌛",
                response_type=ResponseType.UPDATE_MESSAGE).output()
        elif action_method == self.ActionMethod.REFRESH_TIMESHEET_DATA:
            self.handle_event_asynchronously(event)
            return Message(
                text="Getting latest timesheet data... ⌛",
                response_type=ResponseType.UPDATE_MESSAGE).output()

class TimmyAsyncHandler(TimmyBaseHandler):

    def handle_message(self, message, event):
        message_text = message['text'].lower()
        if message_text in ['remind_everyone', 'remind_everyone_meme']:
            spaces = models.Space.scan()
            for space in spaces:
                user = models.User.get(space.username)
                if message_text == 'remind_everyone':
                    message = Message(text=(
                        f"Hey {user.given_name}! Just a friendly reminder "
                        "that it's time to do your timesheet 😄")).output()
                elif message_text == 'remind_everyone_meme':
                    message = MessageTemplate.reminder_meme().output()
                self.chat.create_message(message=message, space_name=space.name)

    def handle_card_clicked(self, action_method, parameters, event):
        if action_method == self.ActionMethod.COPY_TIMESHEET:
            return self.process_copy_timesheet(parameters, event)
        elif action_method == self.ActionMethod.SHOW_THIS_WEEKS_TIMESHEET:
            response = self.process_show_this_weeks_timesheet(parameters, event)
        elif action_method == self.ActionMethod.SHOW_LAST_WEEKS_TIMESHEET:
            response = self.process_show_last_weeks_timesheet(parameters, event)
        elif action_method == self.ActionMethod.PROPOSE_TIMESHEET:
            response = self.process_propose_timesheet(parameters, event)
        elif action_method == self.ActionMethod.REFRESH_TIMESHEET_DATA:
            response = self.process_refresh_timesheet_data(parameters, event)
        if response:
            # Update original message
            self.chat.update_message(event['message']['name'], response)

    def process_copy_timesheet(self, parameters, event):
        start_date = dateparser(parameters.get('start_date')) - timedelta(days=7)
        end_date = dateparser(parameters.get('end_date')) - timedelta(days=7)
        user = models.User.get(event['user']['name'])
        # TODO: Get from DynamoDB instead
        timesheet = user.get_timesheet(start_date=start_date, end_date=end_date)
        new_timesheet = utils.copy_timesheet(timesheet, add_days=7)
        api = user.get_api_and_login()
        api.post_timesheet(new_timesheet)

    def process_show_this_weeks_timesheet(self, parameters, event):
        start_date, end_date = utils.get_week_dates(weeks=0)
        user = models.User.get(event['user']['name'])
        date_entries = self._get_timesheet_date_entries(
            start_date, end_date, user)
        message = MessageTemplate.timesheet_card(date_entries, user=user).output()
        return message

    def process_show_last_weeks_timesheet(self, parameters, event):
        start_date, end_date = utils.get_week_dates(weeks=-1)
        user = models.User.get(event['user']['name'])
        date_entries = self._get_timesheet_date_entries(
            start_date, end_date, user)
        message = MessageTemplate.timesheet_card(date_entries, user=user).output()
        return message

    def process_propose_timesheet(self, parameters, event):
        # Get last week's timesheet
        start_date, end_date = utils.get_week_dates(weeks=-1)
        user = models.User.get(event['user']['name'])
        date_entries = self._get_timesheet_date_entries(
            start_date, end_date, user)
        # Copy timesheet forward
        # TODO: Use `utils.copy_timesheet` and ensure descriptions copied
        new_date_entries = {}
        for dt, entries in date_entries.items():
            new_date = dt + timedelta(days=7)
            new_date_entries[new_date] = entries
        message = MessageTemplate.timesheet_card(
            new_date_entries,
            user=user,
            title='Proposed Timesheet',
            show_buttons=True).output()
        return message

    def process_refresh_timesheet_data(self, parameters, event):
        start_date, end_date = utils.get_week_dates(weeks=-3, week_span=4)
        user = models.User.get(event['user']['name'])
        date_entries = self._get_timesheet_date_entries(
            start_date, end_date, user)
        models.Timesheet.bulk_create_from_date_entries(user=user, date_entries=date_entries)
        message = Message(text="Timesheet data refreshed!").output()
        return message

    def _get_timesheet_date_entries(self, start_date, end_date, user):
        timesheet_api = user.get_api_and_login()
        timesheet = timesheet_api.get_timesheet(
            start_date=start_date,
            end_date=end_date)
        return timesheet.date_entries()


class MessageTemplate:

    @staticmethod
    def action_card():
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
                        TextButton(text="VIEW LAST WEEK'S TIMESHEET").add_action(
                            action_method=ActionMethod.SHOW_LAST_WEEKS_TIMESHEET)),
                    TextParagraph("Show last week's timesheet")),
                Section(
                    ButtonList(
                        TextButton(text="VIEW THIS WEEK'S TIMESHEET").add_action(
                            action_method=ActionMethod.SHOW_THIS_WEEKS_TIMESHEET)),
                    TextParagraph("Show this week's timesheet")),
                Section(
                    ButtonList(
                        TextButton(text="PROPOSE THIS WEEK'S TIMESHEET").add_action(
                            action_method=ActionMethod.PROPOSE_TIMESHEET)),
                    TextParagraph(
                        "Show Timmy's Best Guess™ at this week's timesheet. "
                        "You also have the option to make it real by updating your timesheet "
                        "right from this here chat. Rock on 🤘")),
                Section(
                    TextParagraph('Bring up this menu anytime by typing <b>help</b>')
                )
        ))
        return message

    @staticmethod
    def reminder_meme():
        random_integer = randint(0, 4) + 1
        meme_url = f'https://timesheets.servian.fun/images/{random_integer}.jpg'
        message = Message()
        message.add_card(Card(Section(Image(image_url=meme_url))))
        return message

    @staticmethod
    def timesheet_updated_successfully():
        message = Message(action_response=Message.ResponseType.UPDATE_MESSAGE)
        message.add_card(
            Card(
                Section(
                    TextParagraph('Timesheet updated sucessfully 🎉'),
                    ButtonList(
                        TextButton('VIEW ON TIMESHEETS.COM.AU').add_link('https://timesheets.com.au/login.asp'))),
                Section(
                    ButtonList(
                        TextButton('BACK').add_action(ActionMethod.HELP)))))
        return message

    @staticmethod
    def simple_text_card(text, show_menu_button=False, button_label="BACK"):
        message = Message()
        card = Card(Section(TextParagraph(text)))
        if show_menu_button:
            card.add_section(
                Section(ButtonList(TextButton(button_label).add_action(ActionMethod.HELP))))
        message.add_card(card)
        return message

    @staticmethod
    def timesheet_card(date_entries, user, title='Timesheet Summary', show_buttons=False):
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
        back_button = Section(
            ButtonList(
                TextButton('BACK').add_action(ActionMethod.HELP)))
        card.add_section(back_button)
        message.add_card(card)
        return message
