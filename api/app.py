import json
import logging
import os
from datetime import date, timedelta

from chalice import Chalice, Response
from google.oauth2 import credentials

from dateutil.parser import parse as dateparser

from ssm_parameter_store import EC2ParameterStore
from timepro_timesheet.api import TimesheetAPI, Timesheet

from chalicelib import models, utils, auth, messages

# Logging

logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{levelname:.1} [{asctime} {filename}:{lineno}] {message}')

# Get application configuration from SSM Parameter Store
store = EC2ParameterStore(region_name='ap-southeast-2')
parameters = store.get_parameters_by_path('/team2/', strip_path=True)
EC2ParameterStore.set_env(parameters)  # add parameters to os.environ before calling Chalice()

# Service Outputs

SQS_PARAMETERS = json.loads(os.environ["sqs_terraform_outputs"])

# Google credentials
Credentials = credentials.Credentials

# Initiate app
app = Chalice(app_name='timesheet-bot', debug=True)


# Routes
@app.route('/')
def index():
    request = app.current_request
    logging.info(request.__dict__)
    return {
        'base_url': utils.get_base_url(request),
        'current_url': utils.get_current_url(request)
    }


@app.route('/bot', methods=['POST'])
def bot_event():
    """Handler for events from Hangouts Chat."""
    request = app.current_request
    event = request.json_body
    space_name = event['space']['name']
    space_type = event['space']['type']
    user_name = event['user']['name']

    if event['type'] == 'ADDED_TO_SPACE':
        # Register new space in DB
        space = models.Space(space_name, type=space_type, username=user_name)
        space.save()
        print(f'Registered {space_name} to DynamoDB')
        # Prompt registration
        if event['space']['type'] == 'DM':
            return messages.create_initial_card()

    if event['type'] == 'MESSAGE' or (
            event['type'] == 'ADDED_TO_SPACE' and 'message' in event):
        message_text = event['message']['text']
        if message_text.lower() == 'login':
            resp = check_user_authenticated(event)
        elif message_text.lower() == 'get_last_weeks_timesheet':
            user = models.User.get(user_name)
            message_body = {
                "username": user.username,
                "message_text": message_text.lower()
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "I'm off to track down last week's timesheet!"
            }
        elif message_text.lower() == 'get_current_timesheet':
            user = models.User.get(user_name)
            message_body = {
                "username": user.username,
                "message_text": message_text.lower()
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "I'm off to track down this week's timesheets!"
            }
        elif message_text.lower() == 'get_proposed_timesheet':
            user = models.User.get(user_name)
            message_body = {
                "username": user.username,
                "message_text": message_text.lower()
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "Thinking cap is on! I'm off to divine this week's timesheet!"
            }
        elif message_text.lower() == 'scrape_update_dynamo_db':
            user = models.User.get(user_name)
            message_body = {
                "username": user.username,
                "message_text": message_text.lower()
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "Going to update dynamodb with your hardwork"
            }
        elif message_text.lower() == 'logout':
            logout_success = auth.logout(user_name)
            if logout_success:
                return {'text': "You've been logged out and your TimePro credentials deleted."}
            else:
                return {'text': 'You are currently not logged in.'}
        else:
            resp = messages.create_card_response(message_text)

    elif event['type'] == 'CARD_CLICKED':
        action_name = event['action']['actionMethodName']
        parameters = event['action']['parameters']
        if action_name == messages.COPY_TIMESHEET_ACTION:
            # TODO: Put this all in an SQS queue so we can return
            # a synchronous response to the chat ASAP
            start_date = None
            end_date = None
            if parameters[0]['key'] == 'start_date':
                start_date = dateparser(parameters[0]['value'])
            if parameters[1]['key'] == 'end_date':
                end_date = dateparser(parameters[0]['value'])
            if start_date is None or end_date is None:
                return
            user = models.User.get(user_name)
            timesheet = user.get_timesheet(start_date=start_date, end_date=end_date)  # TODO: Get from DynamoDB instead
            new_timesheet = utils.copy_timesheet(timesheet, add_days=7)
            api = user.get_api_and_login()
            api.post_timesheet(new_timesheet)
            resp = messages.create_timesheet_card(new_timesheet.date_entries(), user=user)
            resp['actionResponse'] = 'UPDATE_MESSAGE'

    elif event['type'] == 'REMOVED_FROM_SPACE':
        # Delete space from DB
        try:
            space = models.Space.get(space_name)
            space.delete()
        except models.Space.DoesNotExist:
            pass
        # Logout user (delete from DB and invalidate token)
        auth.logout(user_name)
        return {}

    logging.info(resp)
    return resp


@app.route('/auth/callback')
def sqs_trigger():
    request = app.current_request
    if request.query_params and request.query_params.get('error'):
        redirect_location = 'https://timesheets.servian.fun/register/error?error=123&state=abc'
    else:
        user = auth.on_oauth2_callback(request)
        redirect_location = 'https://timesheets.servian.fun/register/config'
    if request.query_params and request.query_params.get('state'):
        state = request.query_params.get('state')
        redirect_location += '?state=' + state
    return Response(
        status_code=301,
        body='',
        headers={'Location': redirect_location})


@app.route('/timepro/config', methods=['POST'], cors=True)
def timepro_config():
    request = app.current_request
    data = request.json_body
    api = TimesheetAPI()
    try:
        api.login(
            customer_id=data['customer'],
            username=data['username'],
            password=data['password'])
        oauth2_callback_args = auth.OAuth2CallbackCipher.decrypt(data['state'])
        username = oauth2_callback_args['user_name']
        user_register = models.UserRegister(
            username,
            timepro_username=data['username'],
            timepro_password=data['password'],
            timepro_customer=data['customer'])
        user_register.save()
    except api.LoginError as e:
        return Response(body={'error': str(e)}, status_code=403)
    except Exception as e:
        return Response(body={'error': 'An error occured when validating TimePro credentials'}, status_code=400)
    return request.json_body


def check_user_authenticated(event: dict) -> dict:
    """Handles a mention from Hangouts Chat."""
    request = app.current_request
    user_name = event['user']['name']
    try:
        user = models.User.get(user_name)
    except models.User.DoesNotExist:
        logging.info('Requesting credentials for user %s', user_name)
        oauth2_url = auth.get_authorization_url(event, request)
        return {
            'actionResponse': {
                'type': 'REQUEST_CONFIG',
                'url': oauth2_url,
            }
        }
    user_credentials = user.get_credentials()
    logging.info('Found existing auth credentials for user %s', user_name)
    return {
        'text': "You're authenticated! As soon as we validate your TimePro credentials we'll lookup your timesheet ⏱ 👍"
    }


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_chat_name"])
def sqs_chat_handler(event):
    for record in event:
        payload = json.loads(record.body)
        space_name = payload.get('space_name')
        message = payload.get('message')
        messages.send_async_message(message, space_name)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_process_name"])
def sqs_process_handler(event):
    """
        {
            "username" : email,
            "message_text" : string
        }
    :param event:
    :return:
    """
    pass


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_scrape_name"])
def sqs_scrape_handler(event):
    """
        {
            "username" : chat username (users/12312312)
        }
    :param event:
    :return:
    """
    for record in event:
        payload = json.loads(record.body)
        username = payload["username"]
        message_text = payload["message_text"]
        user = models.User.get(username)
        api = user.get_api_and_login()


        # Get last week -- if Saturday or Sunday, treat "last week" as the week just been
        start_date, end_date = utils.get_last_week_dates() \
            if message_text in ["get_last_weeks_timesheet", "scrape_update_dynamo_db"] else utils.get_this_week_dates()

        timesheet = api.get_timesheet(start_date=start_date, end_date=end_date)
        date_entries = timesheet.date_entries()

        if message_text == "scrape_update_dynamo_db":
            print(f'Looping through timesheet dates for user: {username}')
            for date, entries in date_entries.items():
                print(f'Getting date: {date}')
                json_entries = {'entries': entries}
                timesheet_entry = models.Timesheet(username, date, entries=json_entries, email=user.email)
                timesheet_entry.save()

        message = messages.create_timesheet_card(date_entries, user=user, buttons=True) \
            if message_text == "get_proposed_timesheet" else messages.create_timesheet_card(date_entries, user=user)
        space_name = models.Space.get_from_username(username)
        messages.send_async_message(message, space_name=space_name)
