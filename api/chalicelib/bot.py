from . import models, utils, auth, messages


class BotHandler:
    def __init__(self, event):
        self._response = None
        self.event = event
        self.event_type = event_type = event['type']
        self.space_name = event['space']['name']
        self.space_type = event['space']['type']
        self.username = event['user']['name']

        # New space
        if event_type == 'ADDED_TO_SPACE' and 'message' in event:
            # Added to room
            self.handle_added_to_space()
        elif event_type == 'ADDED_TO_SPACE':
            # Added to DM
            self.handle_added_to_space()
        elif event_type == 'REMOVED_FROM_SPACE':
            self.handle_removed_from_space()

        # Handle message
        if event_type == 'CARD_CLICKED':
            self.handle_card_clicked()
        elif event_type == 'MESSAGE' or \
                event_type == 'ADDED_TO_SPACE' and 'message' in event:
            message = event['message']['text']
            self.handle_message(message)

    def get_response(self):
        if self._response is None:
            return {}
        return self._response

    def handle_message(self, message):
        pass

    def handle_card_clicked(self):
        pass

    def handle_added_to_space(self):
        # Register new space in DB
        space = models.Space(self.space_name, type=self.space_type, username=self.username)
        space.save()
        self.space = space
        # Prompt registration
        if self.event_type == 'DM':
            return messages.create_initial_card()

    def handle_removed_from_space(self):
        try:
            space = models.Space.get(self.space_name)
            space.delete()
        except models.Space.DoesNotExist:
            pass  # doesn't exist, no point deleting
        auth.logout(self.username)  # delete user from DynamoDB and invalidate token
