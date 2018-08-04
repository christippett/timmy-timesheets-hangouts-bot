import json

from chalice import Chalice

app = Chalice(app_name='timesheet-bot')


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/bot', methods=['POST'])
def bot_event():
    """Handler for events from Hangouts Chat."""
    request = app.current_request
    event = request.json_body
    json_string = json.dumps(event, indent=2)
    if event['type'] == 'MESSAGE' or (
            event['type'] == 'ADDED_TO_SPACE' and 'message' in event):
        return { 'text':  json_string }
    elif event['type'] == 'ADDED_TO_SPACE':
        # Added via DM
        # TODO: Register conversation with DynamoDB
        return { 'text':  json_string }
    elif event_data['type'] == 'CARD_CLICKED':
        action_name = event_data['action']['actionMethodName']
        parameters = event_data['action']['parameters']
        return { 'text':  json_string }
    elif event['type'] == 'REMOVED_FROM_SPACE':
        # TODO: Delete converation ID fom DynamoDB
        pass


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
