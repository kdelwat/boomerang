import uvloop

from sanic import Sanic
import sanic.response as response

from . import events


class Messenger:
    '''The base class that contains the Facebook Messenger bot, and handles
    webhooks and sending.

    The application should subclass this class and override the webhook handler
    methods as required.

    Attributes:
       verify_token: The string Messenger Platform verify token.
       page_token: The string Messenger Platform page access token.

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
                server_response = await self.handle_webhook(request)
                return server_response

    def run(self, hostname='127.0.0.1', port=8000, debug=False):
        '''Runs the bot using the given server settings.

        Args:
            hostname: A string representing the hostname on which to run the
                      server.
            port: The integer port on which to run the server.
            debug: A boolean enabling debug logging during operation.

        Returns:
            None

        '''
        self._server.run(loop=self._event_loop,
                         host=hostname,
                         port=port,
                         debug=debug)

    def register(self, request):
        '''Handles registration of the Messenger Platform using the webhook system.

        Args:
            request: A request object passed by the Sanic server.

        Returns:
            A Sanic text response. If registration was successful, the provided
            challenge string is returned with a 200 OK status. However, if the
            verification token does not match the class' token, a 403 FORBIDDEN
            request is returned.

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

    async def handle_webhook(self, request):
        '''Handles all POST requests made to the /webhook endpoint by the Messenger
        Platform.

        The request is formatted and delegated to the relevant
        user-implementable event functions.

        Args:
            request: A request object passed by the Sanic server.

        Returns:
            A Sanic text response. If the request was successfully handled,
            the response is 200 OK.

        '''
        # The API provides a list of events inside of the 'entry' list
        for event in request.json['entry']:

            # Inside the event is a list of messages, under 'messaging'
            for message in event['messaging']:

                # Isolate the User ID and timestamp, which are both present
                # regardless of message type
                user_id = int(message['sender']['id'])
                timestamp = message['timestamp']

                # Each message type has an identifier, which Facebook uses to
                # signify the type; a class, for holding the message; and a
                # handler function which is implemented by the user.
                message_types = [('message', events.MessageReceived,
                                  self.message_received),
                                 ('delivery', events.MessageDelivered,
                                  self.message_delivered),
                                 ('read', events.MessageRead,
                                  self.message_read),
                                 ('postback', events.Postback,
                                  self.postback),
                                 ('referral', events.Referral,
                                  self.referral),
                                 ('optin', events.OptIn,
                                  self.opt_in),
                                 ('account_linking', events.AccountLink,
                                  self.account_link)]

                # Loop through the message types. If one is found, create the
                # relevant message object and handle it. Then break from the
                # loop as there can only be one type present at a time.
                for message_type in message_types:
                    identifier, message_class, handler = message_type

                    if identifier in message:
                        event = message_class.from_json(user_id,
                                                        timestamp,
                                                        message[identifier])
                        await handler(event)
                        break

        return response.text('Success', status=200)

    async def message_received(self, message):
        '''Handles all 'message received' events sent to the bot.

        Args:
            message: A MessageReceived object containing the received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling received message')

    async def message_delivered(self, message_delivered):
        '''Handles all 'message delivered' events sent to the bot.

        Args:
            message_delivered: A MessageDelivered object containing the
                               received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling delivered message')

    async def message_read(self, message_read):
        '''Handles all 'message read' events sent to the bot.

        Args:
            message_read: A MessageRead object containing the
                          received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling read message')

    async def postback(self, postback):
        '''Handles all 'postback' events sent to the bot.

        Args:
            postback: A Postback object containing the
                      received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling postback')

    async def referral(self, referral):
        '''Handles all 'referral' events sent to the bot.

        Args:
            referral: A Referral object containing the
                      received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling referral')

    async def opt_in(self, opt_in):
        '''Handles all 'opt in' events sent to the bot.

        Args:
            opt_in: An OptIn object containing the
                    received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling opt in')

    async def account_link(self, account_link):
        '''Handles all 'account linking' events sent to the bot.

        Args:
            opt_in: An AccountLink object containing the
                    received message.

        Returns:
            None. The message should be completely handled within this
            function.

        '''
        print('Handling account linking')
