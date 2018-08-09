import json
import logging
import os
from datetime import date, timedelta

from chalice import Chalice, Response, Rate
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
            return messages.create_action_card()

    if event['type'] == 'MESSAGE' or (
            event['type'] == 'ADDED_TO_SPACE' and 'message' in event):
        message_text = event['message']['text'].lower()

        user_authenticated, resp = check_user_authenticated(event)
        if not user_authenticated:
            return resp

        if message_text == 'login':
            user_authenticated, resp = check_user_authenticated(event)
            if user_authenticated:
                resp = {'text': "You're already authenticated 👍"}
        elif message_text == 'help':
            resp = messages.create_action_card()
        elif message_text in ['remind_everyone', 'remind_everyone_meme']:
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_process_id"], message=event)
            resp = {'text': 'Sending a reminder to everyone!'}
        elif message_text == 'get_last_weeks_timesheet':
            message_body = {
                "username": user_name,
                "message_text": message_text
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "I'm off to track down last week's timesheet!"
            }
        elif message_text == 'get_current_timesheet':
            message_body = {
                "username": user_name,
                "message_text": message_text
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "I'm off to track down this week's timesheets!"
            }
        elif message_text == 'get_proposed_timesheet':
            message_body = {
                "username": user_name,
                "message_text": message_text
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "Thinking cap is on! I'm off to divine this week's timesheet!"
            }
        elif message_text == 'scrape_update_dynamo_db':
            message_body = {
                "username": user_name,
                "message_text": message_text
            }
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            return {
                'text': "Going to update dynamodb with your hardwork"
            }
        elif message_text == 'logout':
            logout_success = auth.logout(user_name)
            if logout_success:
                return {'text': "You've been logged out and your TimePro credentials deleted."}
            else:
                return {'text': 'You are currently not logged in.'}
        else:
            resp = messages.create_action_card()

    elif event['type'] == 'CARD_CLICKED':
        action_name = event['action']['actionMethodName']
        if action_name == messages.COPY_TIMESHEET_ACTION:
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_process_id"], message=event)
            resp = messages.create_timesheet_success_card()
        elif action_name == messages.ActionMethod.HELP.value:
            resp = messages.create_action_card()
        elif action_name == messages.ActionMethod.LOGIN.value:
            user_authenticated, resp = check_user_authenticated(event)
            if user_authenticated:
                return resp
            resp = {'text': "You're already authenticated 👍"}
        elif action_name == messages.ActionMethod.SHOW_THIS_WEEKS_TIMESHEET.value:
            message_body = {"username": user_name, "message_text": 'get_current_timesheet'}
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            resp = messages.create_card_response("I'm off to track down this week's timesheet... ⌛")
        elif action_name == messages.ActionMethod.SHOW_LAST_WEEKS_TIMESHEET.value:
            message_body = {"username": user_name, "message_text": 'get_last_weeks_timesheet'}
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            resp = messages.create_card_response("I'm off to track down last week's timesheet... ⌛")
        elif action_name == messages.ActionMethod.PROPOSE_TIMESHEET.value:
            message_body = {"username": user_name, "message_text": 'get_proposed_timesheet'}
            utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=message_body)
            resp = messages.create_card_response("Thinking cap is on! I'm off to divine this week's timesheet... ⌛")
        # Update message instead of sending a new message
        resp['actionResponse'] = {'type': 'UPDATE_MESSAGE'}
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


@app.route('/debug/message', methods=['POST'])
def debug_message():
    """
        Forward messages received to this endpoint to the user matching the
        email address in the header
    """
    request = app.current_request
    data = request.json_body
    email = request.headers.get('USER_EMAIL')
    try:
        space = models.Space.get_from_email(email)
        payload = {
            'space_name': space.name,
            'message': data
        }
        utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_chat_id"], message=payload)
        return {'success': 'Message sent'}
    except Exception as e:
        return {'error': str(e)}


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
            timepro_customer=data['customer'])
        user_register.timepro_password = data['password']
        user_register.save()
    except api.LoginError as e:
        return Response(body={'error': str(e)}, status_code=403)
    except Exception as e:
        return Response(body={'error': 'An error occured when validating TimePro credentials'}, status_code=400)
    # Send async success message
    space = models.Space.get_from_username(username)
    payload = {
        'space_name': space.name,
        'message': {
            'text': "You're authenticated and your TimePro credentials have been configured. You're on fire! 🔥"}
    }
    utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_chat_id"], message=payload)
    return request.json_body


def check_user_authenticated(event: dict) -> dict:
    """Handles a mention from Hangouts Chat."""
    request = app.current_request
    user_name = event['user']['name']
    try:
        user = models.User.get(user_name)
        user_register = models.UserRegister.get(user_name)
    except (models.User.DoesNotExist, models.UserRegister.DoesNotExist):
        logging.info('Requesting credentials for user %s', user_name)
        oauth2_url = auth.get_authorization_url(event, request)
        return False, {
            'actionResponse': {
                'type': 'REQUEST_CONFIG',
                'url': oauth2_url,
            }
        }
    logging.info('Found existing auth credentials for user %s', user_name)
    return True, None


@app.schedule(Rate(20, unit=Rate.MINUTES))
def warming_sqs_lambda_functions(event):
    payload = {
        "warming": True
    }
    utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_chat_id"], message=payload)
    utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_process_id"], message=payload)
    utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"], message=payload)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_chat_name"])
def sqs_chat_handler(sqs_event):
    for record in sqs_event:
        payload = json.loads(record.body)
        if payload.get("warming"):
            logging.info("Warming up sqs_chat_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        space_name = payload.get('space_name')
        message = payload.get('message')
        messages.send_async_message(message, space_name)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_process_name"])
def sqs_process_handler(sqs_event):
    for record in sqs_event:
        event = json.loads(record.body)
        if event.get("warming"):
            logging.info("Warming up sqs_process_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        user_name = event['user']['name']
        # TODO: Use a single event handler for both sync and async responses
        if event['type'] == 'MESSAGE' and event['message']['text'].lower() in ['remind_everyone',
                                                                                'remind_everyone_meme']:
            spaces = models.Space.scan()
            for space in spaces:
                user = models.User.get(space.username)
                if event['message']['text'].lower() == 'remind_everyone':
                    message = {
                        'text': f"Hey {user.given_name}! Just a friendly reminder that it's time to do your timesheet 😄"}
                else:
                    message = messages.create_reminder_meme()
                payload = {
                    'space_name': space.name,
                    'message': message
                }
                utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_chat_id"], message=payload)
        elif event['type'] == 'CARD_CLICKED':
            action_name = event['action']['actionMethodName']
            parameters = event['action']['parameters']
            if action_name == messages.COPY_TIMESHEET_ACTION:
                start_date = None
                end_date = None
                if parameters[0]['key'] == 'start_date':
                    start_date = dateparser(parameters[0]['value']) - timedelta(days=7)
                if parameters[1]['key'] == 'end_date':
                    end_date = dateparser(parameters[1]['value']) - timedelta(days=7)
                if start_date is None or end_date is None:
                    return
                user = models.User.get(user_name)
                timesheet = user.get_timesheet(start_date=start_date,
                                                end_date=end_date)  # TODO: Get from DynamoDB instead
                new_timesheet = utils.copy_timesheet(timesheet, add_days=7)
                api = user.get_api_and_login()
                api.post_timesheet(new_timesheet)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_scrape_name"])
def sqs_scrape_handler(sqs_event):
    """
        {
            "username" : chat username (users/12312312)
        }
    :param sqs_event:
    :return:
    """
    for record in sqs_event:
        payload = json.loads(record.body)
        if payload.get("warming"):
            logging.info("Warming up sqs_scrape_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        username = payload["username"]
        message_text = payload["message_text"]
        user = models.User.get(username)
        api = user.get_api_and_login()

        if message_text in ["get_last_weeks_timesheet", "scrape_update_dynamo_db", "get_proposed_timesheet"]:
            start_date, end_date = utils.get_week_dates(weeks=-1)
        else:
            start_date, end_date = utils.get_week_dates(weeks=0)

        timesheet = api.get_timesheet(start_date=start_date, end_date=end_date)
        date_entries = timesheet.date_entries()

        if message_text == "scrape_update_dynamo_db":
            print(f'Looping through timesheet dates for user: {username}')
            models.Timesheet.bulk_create_from_date_entries(user=user, date_entries=date_entries)
            message = {"text": "Updated your work history in DyDb!!"}
        elif message_text == "get_proposed_timesheet":
            new_date_entries = {}
            for date, entries in date_entries.items():
                new_date = date + timedelta(days=7)
                new_date_entries[new_date] = entries
            message = messages.create_timesheet_card(
                new_date_entries,
                user=user,
                title='Proposed Timesheet',
                show_buttons=True)
        else:
            message = messages.create_timesheet_card(date_entries, user=user)

        space = models.Space.get_from_username(username)
        messages.send_async_message(message, space_name=space.name)
