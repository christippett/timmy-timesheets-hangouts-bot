import json
import logging
import os
from datetime import date, timedelta

from chalice import Chalice, Response, Rate
from google.oauth2 import credentials

from dateutil.parser import parse as dateparser

from ssm_parameter_store import EC2ParameterStore
from timepro_timesheet.api import TimesheetAPI, Timesheet
from hangouts_helper.api import HangoutsChatAPI

from chalicelib import models, utils, auth, bot


# Logging
logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{levelname:.1} [{asctime} {filename}:{lineno}] {message}')


def get_parameters():
    store = EC2ParameterStore(region_name='ap-southeast-2')
    parameters = store.get_parameters_by_path('/team2/', strip_path=True)
    EC2ParameterStore.set_env(parameters)
    parameters.update({
        'sqs_parameters': json.loads(parameters.get('sqs_terraform_outputs')),
        'google_auth_client_secret': json.loads(parameters.get('google_auth_client_secret')),
        'google_auth_service_account': json.loads(parameters.get('google_auth_service_account')),
        'config_callback_url': 'https://api.timesheets.servian.fun/v1/auth/callback'
    })
    return parameters

DEBUG = True
PARAMETERS = get_parameters()
SQS_PARAMETERS = PARAMETERS.get('sqs_parameters')

# Initiate app
app = Chalice(app_name='timesheet-bot', debug=DEBUG)


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
    timmy = bot.TimmySyncHandler(parameters=PARAMETERS, debug=DEBUG)
    event = app.current_request.json_body
    return timmy.handle_chat_event(event)


@app.route('/debug/message', methods=['POST'])
def debug_message():
    """Forward messages received to this endpoint to the user matching the
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
        utils.sqs_send_message(
            queue_url=PARAMETERS['sqs_parameters']["sqs_queue_chat_id"],
            message=payload)
        return {'success': 'Message sent'}
    except Exception as e:
        return {'error': str(e)}


@app.route('/auth/callback')
def oauth_callback():
    request = app.current_request
    if request.query_params and request.query_params.get('error'):
        redirect_location = 'https://timesheets.servian.fun/register/error'
    else:
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        auth.on_oauth2_callback(
            callback_url=PARAMETERS.get('config_callback_url'),
            state=state,
            code=code,
            client_secret=PARAMETERS.get('google_auth_client_secret'))
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
    # space = models.Space.get_from_username(username)
    # payload = {
    #     'space_name': space.name,
    #     'message': {
    #         'text': "You're authenticated and your TimePro credentials have been configured. You're on fire! 🔥"}
    # }
    # utils.sqs_send_message(queue_url=SQS_PARAMETERS["sqs_queue_chat_id"], message=payload)
    return request.json_body


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_process_name"])
def sqs_process_handler(sqs_event):
    for record in sqs_event:
        event = json.loads(record.body)
        if event.get("warming"):
            logging.info("Warming up sqs_process_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        timmy = bot.TimmyAsyncHandler(parameters=PARAMETERS, debug=DEBUG)
        return timmy.handle_chat_event(event)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_chat_name"])
def sqs_chat_handler(sqs_event):
    for record in sqs_event:
        payload = json.loads(record.body)
        if payload.get("warming"):
            logging.info("Warming up sqs_chat_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        space_name = payload.get('space_name')
        message = payload.get('message')
        chat = HangoutsChatAPI(PARAMETERS.get('google_auth_service_account'))
        chat.create_message(message, space_name)


@app.schedule(Rate(20, unit=Rate.MINUTES))
def warming_sqs_lambda_functions(event):
    payload = {"warming": True}
    utils.sqs_send_message(
        queue_url=SQS_PARAMETERS["sqs_queue_chat_id"],
        message=payload)
    utils.sqs_send_message(
        queue_url=SQS_PARAMETERS["sqs_queue_process_id"],
        message=payload)
    utils.sqs_send_message(
        queue_url=SQS_PARAMETERS["sqs_queue_scrape_id"],
        message=payload)


@app.on_sqs_message(queue=SQS_PARAMETERS["sqs_queue_scrape_name"])
def sqs_scrape_handler(sqs_event):
    """Scrape user's timesheets and save to database
    """
    for record in sqs_event:
        payload = json.loads(record.body)
        if payload.get("warming"):
            logging.info("Warming up sqs_scrape_handler lambda.")
            continue  # skip further processing if triggered by warmup function
        # TODO: Loop through `models.UserRegister`` and scrape each user's timesheet
