import uvloop

from sanic import Sanic
import sanic.response as response

from . import messages


class Messenger:
    '''The Messenger class is the base class that contains the Facebook Messenger
    bot, and handles webhooks and sending. The application should subclass
    Messenger and override the webhook handler methods as required.

    .. py:class:: Messenger(verify_token, page_token)

       :param str verify_token: The Messenger Platform verify token.
       :param str page_token: The Messenger Platform page access token.

    '''
    def __init__(self, verify_token, page_token):
        self._verify_token = verify_token
        self._page_token = page_token

        self._event_loop = uvloop.new_event_loop()
        self._server = Sanic(__name__)

        # Create a handler for the webhook which delegates to different
        # functions depending on the HTTP method used. GET requests are used
        # by Messenger to validate the bot, while POST requests are used to
        # send the bot events.
        @self._server.route('/webhook', methods=['GET', 'POST'])
        async def webhook(request):
            if request.method == 'GET':
                server_response = self.register(request)
                return server_response
            elif request.method == 'POST':
                server_response = self.handle_webhook(request)
                return server_response

    def run(self, hostname='127.0.0.1', port=8000, debug=False):
        '''Run the bot using the given server settings.

        :param str hostname: The hostname on which to run the server.
        :param int port: The port on which to run the server.
        :param bool debug: Enable debug logging during operation.

        '''
        self._server.run(loop=self._event_loop,
                         host=hostname,
                         port=port,
                         debug=debug)

    def register(self, request):
        '''Handles registration of the Messenger Platform using the webhook system.

        :param request: A request object passed by the Sanic server.

        '''
        request_type = request.args['hub.mode'][0]
        request_verify_token = request.args['hub.verify_token'][0]
        request_challenge = request.args['hub.challenge'][0]

        is_verified = (request_verify_token == self._verify_token)

        if request_type == 'subscribe':
            if is_verified:
                return response.text(request_challenge, status=200)
            else:
                return response.text('Verification token did not match server',
                                     status=403)

    def handle_webhook(self, request):
        '''Handles all POST requests made to the /webhook endpoint by the Messenger
        Platform. The request is formatted and delegated to the relevant
        user-implementable event functions.

        :param request: A request object passed by the Sanic server.

        '''
        # The API provides a list of events inside of the 'entry' list
        for event in request.json['entry']:

            # Inside the event is a list of messages, under 'messaging'
            for message in event['messaging']:

                # Isolate the User ID and timestamp, which are both present
                # regardless of message type
                user_id = int(message['sender']['id'])
                timestamp = message['timestamp']

                # Delegate received message event to user function
                if 'message' in message:
                    message_obj = messages.Message.from_json(user_id,
                                                             timestamp,
                                                             message['message'])
                    self.message_received(message_obj)

                else:
                    print(user_id, message)

        return response.text('Success', status=200)

    def message_received(self, message):
        '''Receives all messages sent to the bot, enclosed in the Message class.
        The user defines this function with no return value.

        :param message: A Message object.

        '''
        print('Handling received message')
