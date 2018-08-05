import json
import re
import logging

import boto3
from dateutil.parser import parse as dateparser
from dateutil.relativedelta import relativedelta, MO, FR
from datetime import date


session = boto3.session.Session(region_name="ap-southeast-2")


def get_base_url(current_request, path=None):
    headers = current_request.headers
    proto = headers.get('x-forwarded-proto', 'http')
    host = headers.get('host')
    stage = current_request.context.get('stage', '')
    path = path or ''
    url_path = re.sub(r'/{2,}', '/', f'{host}/{stage}/{path}')
    return f'{proto}://{url_path}'


def get_current_url(current_request, params=True):
    headers = current_request.headers
    proto = headers.get('x-forwarded-proto', 'http')
    host = headers.get('host')
    stage = current_request.context.get('stage', '')
    resource_path = current_request.context.get('resourcePath', '')
    url_path = re.sub(r'/{2,}', '/', f'{host}/{stage}/{resource_path}')
    query_params = current_request.query_params
    if params and query_params:
        query_params_string = '&'.join([f'{k}={v}' for k, v in query_params.items()])
        if query_params_string:
            return f'{proto}://{url_path}?{query_params_string}'
    return f'{proto}://{url_path}'


def get_this_week_dates():
    today = date.today()
    # Get last week -- if Saturday or Sunday, treat "last week" as the week just been
    week_offset = 1 if today.weekday() >= 5 else 0
    start_date = today + relativedelta(weekday=MO(-1), weeks=week_offset - 1)
    end_date = start_date + relativedelta(weekday=FR)
    return start_date, end_date


def sqs_send_message(queue_url: str, message: dict):
    logging.info("Sending message to SQS Queue: {queue_url}".format(queue_url=queue_url))
    sqs_client = session.resource('sqs')
    sqs_queue = sqs_client.Queue(queue_url)
    sqs_queue.send_message(MessageBody=json.dumps(message))
