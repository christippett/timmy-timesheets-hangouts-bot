import json
import logging
import os
from datetime import date, timedelta

import boto3
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

session = boto3.session.Session(region_name="ap-southeast-2")

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
            return {
                'text': 'Hey - thanks for adding me!'
            }

    if event['type'] == 'MESSAGE' or (
            event['type'] == 'ADDED_TO_SPACE' and 'message' in event):
        message_text = event['message']['text']
        if message_text.lower() == 'login':
            resp = check_user_authenticated(event)
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
            resp = copy_timesheet(user_name, parameters)

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
def oauth2_callback():
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
        user = models.User.get(username)
        user_register = models.UserRegister(user.email)
        user_register.timepro_username = data['username']
        user_register.timepro_password = data['password']
        user_register.timepro_customer = data['customer']
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
    return {'text': "You're authenticated and ready to go!"}
    # return produce_profile_message(user_credentials)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_chat_name"])
def sqs_chat_handler(event):
    for record in event:
        payload = json.loads(record.body)
        space_name = payload.get('space_name')
        message = payload.get('message')
        messages.send_async_message(message, space_name)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_scrape_name"])
def sqs_scrape_handler(event):
    """
        {
            "username" : email
        }
    :param event:
    :return:
    """
    print('Starting SQS scraping handler')
    for record in event:
        payload = json.loads(record.body)
        email_username = payload["username"]
        user_register = models.UserRegister.get(email_username)
        user_results = list(models.User.scan(filter_condition=(models.User.email==email_username)))
        if user_results:
            user = user_results[0]
        else:
            user = None
        api = TimesheetAPI()
        api.login(customer_id=user_register.timepro_customer,
                  username=user_register.timepro_username,
                  password=user_register.timepro_password)

        # Get last week -- if Saturday or Sunday, treat "last week" as the week just been
        start_date, end_date = utils.get_this_week_dates()

        timesheet = api.get_timesheet(start_date=start_date, end_date=end_date)
        date_entries = timesheet.date_entries()

        print(f'Looping through timesheet dates for user: {email_username}')
        for date, entries in date_entries.items():
            print(f'Getting date: {date}')
            json_entries = {'entries': entries}
            timesheet_entry = models.Timesheet(email_username, date, entries=json_entries)
            timesheet_entry.save()
        message = messages.create_timesheet_card(date_entries, user=user)
        space_name = get_space_for_email(email_username)
        messages.send_async_message(message, space_name=space_name)


def get_space_for_email(email: str):
    # extract first member of scan, assuming first entry
    username_results = [user.username for user in models.User.scan(filter_condition=(models.User.email==email))]
    if username_results:
        username = username_results[0]
    else:
        username = None

    space_results = [space.name for space in models.Space.scan(filter_condition=(models.Space.username == username))]

    if space_results:
        return space_results[0]
    return None


def copy_timesheet(username, parameters):
    start_date = None
    end_date = None
    if parameters[0]['key'] == 'start_date':
        start_date = dateparser(parameters[0]['value'])
    if parameters[1]['key'] == 'end_date':
        end_date = dateparser(parameters[0]['value'])
    if start_date is None or end_date is None:
        return
    user = models.User.get(username)
    user_register = models.UserRegister.get(user.email)
    api = TimesheetAPI()
    api.login(customer_id=user_register.timepro_customer,
              username=user_register.timepro_username,
              password=user_register.timepro_password)
    start_date, end_date = utils.get_this_week_dates()
    timesheet = api.get_timesheet(start_date=start_date, end_date=end_date)
    date_entries = timesheet.date_entries()
    new_date_entries = {}
    for date, entries in date_entries.items():
        new_date = date + timedelta(days=7)
        new_date_entries[new_date] = entries
    new_timesheet = Timesheet(data=new_date_entries)
    api.post_timesheet(new_timesheet)
