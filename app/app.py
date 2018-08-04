import json

from chalice import Chalice
from ssm_parameter_store import EC2ParameterStore

from chalicelib.models import Space


app = Chalice(app_name='timesheet-bot')
app.debug = True


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/bot', methods=['POST'])
def bot_event():
    """Handler for events from Hangouts Chat."""
    request = app.current_request
    event = request.json_body
    json_string = json.dumps(event, indent=4)
    message_text = event['message']['text']

    if event['type'] == 'ADDED_TO_SPACE':
        # Register new space in DB
        space_name = event['space']['name']
        space_type = event['space']['type']
        space = Space(space_name, type=space_type)
        space.save()
        print(f'Registered {space_name} to DynamoDB')

    if event['type'] == 'MESSAGE' or (
            event['type'] == 'ADDED_TO_SPACE' and 'message' in event):
        if 'param:' in message_text:
            store = EC2ParameterStore(region_name='ap-southeast-2')
            _, param_name = message_text.split(':')
            parameter = store.get_parameter(param_name, decrypt=True)
            return { 'text':  json.dumps(parameter, indent=4) }
        return { 'text':  json_string }
    elif event['type'] == 'CARD_CLICKED':
        action_name = event['action']['actionMethodName']
        parameters = event['action']['parameters']
        return { 'text':  json_string }
    elif event['type'] == 'REMOVED_FROM_SPACE':
        # Delete space from DB
        try:
            space = Space.get(event['space']['name'])
            space.delete()
        except Space.DoesNotExist:
            pass


# @app.on_sqs_message(queue='team2-sqs-app-data-a')
# def handler(event):
#     for record in event:
#         print("Message body: %s" % record.body)


# @app.on_s3_event(bucket='mybucket')
# def handler(event):
#     print("Object uploaded for bucket: %s, key: %s"
#           % (event.bucket, event.key))


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
