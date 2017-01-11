import uvloop
import json
import aiohttp
import hashlib
import functools

from sanic import Sanic
from sanic.log import log
import sanic.response as response

from . import events, messages
from .exceptions import BoomerangException, MessengerAPIException


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

        # A dictionary which holds currently-hosted attachments, where
        # the filename is the key and the relative url is the value.
        self._attachments = {}

        # A dictionary which contains the current handler functions for each
        # message event.
        self._handlers = {}

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

    def run(self, hostname='127.0.0.1', base_url=None, port=8000, debug=False,
            processes=1):
        '''Runs the bot using the given server settings.

        Args:
            hostname: A string representing the hostname on which to run the
                      server.
            base_url: The public url of the bot server, used for tasks such
                      as attachment hosting. If None, these features will not
                      be available.
            port: The integer port on which to run the server.
            debug: A boolean enabling debug logging during operation.
            processes: An integer number of processes to run the server on.

        Returns:
            None

        '''
        self._base_url = base_url
        self._server.run(loop=self._event_loop,
                         host=hostname,
                         port=port,
                         debug=debug,
                         workers=processes)

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
                # signify the type; a class, for holding the message; and an
                # event type constant.
                message_types = [('message', events.MessageReceived,
                                  events.MESSAGE_RECEIVED),
                                 ('delivery', events.MessageDelivered,
                                  events.MESSAGE_DELIVERED),
                                 ('read', events.MessageRead,
                                  events.MESSAGE_READ),
                                 ('postback', events.Postback,
                                  events.POSTBACK),
                                 ('referral', events.Referral,
                                  events.REFERRAL),
                                 ('optin', events.OptIn,
                                  events.OPTIN),
                                 ('account_linking', events.AccountLink,
                                  events.ACCOUNT_LINKING)]

                # Loop through the message types. If one is found, create the
                # relevant message object and handle it. Then break from the
                # loop as there can only be one type present at a time.
                for message_type in message_types:
                    identifier, message_class, event_type = message_type

                    if identifier in message:
                        # Don't respond to echo events
                        if 'is_echo' not in message[identifier]:
                            event = message_class.from_json(user_id,
                                                            timestamp,
                                                            message[identifier])

                            await self.handle_event(event_type, event)
                            break

        return response.text('Success', status=200)

    async def handle_event(self, event_type, event):
        '''Calls each handler of the given event_type with the event object.

        Args:
            event_type: The event type constant, like events.POSTBACK.
            event: The object containing the event.

        Returns:
            None

        '''
        log.info('Handling event with type: {0}'.format(event_type))
        # If the event type has no handlers, exit early
        if event_type not in self._handlers:
            log.warn('No handlers available for the given event')
            return

        for handler_function in self._handlers[event_type]:
            await handler_function(event)

        log.info('Successfully handled event')

    def handle_api_error(self, error_json):
        '''Wraps the error JSON returned by Facebook in a
        MessengerAPIException and raises it.

        Args:
            error_json: A dictionary containing the JSON representation
                        of an error returned by the API.

        Returns:
            None

        Raises:
            MessengerAPIException: Wraps the API error.

        '''
        error_payload = error_json['error']
        error_message = '{0} ({1}): {2}'.format(error_payload['code'],
                                                error_payload['error_subcode'],
                                                error_payload['message'])

        raise MessengerAPIException(error_message)

    async def post(self, session, data, api_endpoint='messages'):
        '''Makes a POST request to the Send API.

        Args:
            session: The aiohttp session to use.
            data: A JSON dictionary that will be the body of the POST request.
            api_endpoint: The endpoint in the Facebook Graph API to post
                          to. The default is 'messages' for the Send API,
                          but it may be changed to allow for thread settings
                          etc.

        Returns:
            An aiohttp response in JSON format.
        '''
        url = 'https://graph.facebook.com/v2.6/me/' \
              + api_endpoint \
              + '?access_token=' \
              + self._page_token
        headers = {'content-type': 'application/json'}

        # Create a JSON string
        json_data = json.dumps(data)

        async with session.post(url, data=json_data, headers=headers) as response:
            return await response.json()

    async def get(self, session, url):
        '''Makes a GET request to the given URL.

        Args:
            session: The aiohttp session to use.
            url: The URL to request from.

        Returns:
            An aiohttp response in JSON format.
        '''
        async with session.get(url) as response:
            return await response.json()

    async def send(self, recipient_id, message):
        '''Sends a message to the given recipient using the Send API.

        Args:
            recipient_id: The integer ID of the user to send the message to.
            message: A Message object containing the message to send.

        Returns:
            The message ID returned by the Send API.

        '''
        # Create the JSON for the POST request.
        json_message = {'recipient': {'id': recipient_id},
                        'message': message.to_json()}

        async with aiohttp.ClientSession(loop=self._event_loop) as session:
            response = await self.post(session, json_message)

        if 'message_id' in response:
            return response['message_id']
        else:
            self.handle_api_error(response)

    async def send_action(self, recipient_id, action):
        '''Sends an action to the given recipient using the Send API.

        Args:
            recipient_id: The integer ID of the user to send the message to.
            action: One of 'typing_on', 'typing_off', or 'mark_seen'.

        Returns:
            The message ID returned by the Send API.

        '''
        if action not in ['typing_on', 'typing_off', 'mark_seen']:
            error = ("Action must be one of 'typing_on', 'typing_off',"
                     "or 'mark_seen', not {0}".format(action))
            raise BoomerangException(error)

        # Create the JSON for the POST request.
        json_message = {'recipient': {'id': recipient_id},
                        'sender_action': action}

        async with aiohttp.ClientSession(loop=self._event_loop) as session:
            response = await self.post(session, json_message)

        if 'recipient_id' in response:
            return response['recipient_id']
        else:
            self.handle_api_error(response)

    async def acknowledge(self, message):
        '''Use message actions to acknowledge to the user that sent the given
        message that the message has been received and is being worked on.

        This function sends both the 'mark_seen' and 'typing_on' events to the
        user. Sending a new message to the user will automatically disable the
        typing notification.

        Args:
            message: A MessageReceived object to acknowledge the receipt of.

        '''
        await self.send_action(message.user_id, 'mark_seen')
        await self.send_action(message.user_id, 'typing_on')

    async def respond_to(self, message_received, response):
        '''Send a new Message to the user who triggered the given MessageReceived
        event.

        Args:
            message_received: A MessageReceived object to respond to.
            response: A Message object to send to the user who triggered
                      message_recieved.

        Returns:
            The message ID returned by the Send API.

        '''
        return await self.send(message_received.user_id, response)

    async def host_attachment(self, media_type, filename):
        '''Hosts the given file on the bot server, returning a MediaAttachment
        object which can be sent to the Messenger API, which will access the
        attachment from the current server.

        Args:
            media_type: The type of the attachment. Can be one of 'image',
                        'audio', 'video' or 'file'.
            filename: The filename of the attachment.

        Returns:
            A MediaAttachment object representing the hosted attachment.
        '''

        # If the base_url isn't set or is None, attachments cannot be hosted
        if self._base_url is None:
            error = 'base_url must be set for attachment hosting'
            raise BoomerangException(error)

        if filename not in self._attachments:
            # The SHA-256 hash of the filename is used as an identifier,
            # which is served as the URL of the attachment. This has two
            # benefits: firstly, it guarantees a unique identifier for
            # different attachments; and secondly, it obfuscates the file
            # structure of the hosting machine for better security.
            identifier = hashlib.sha256(bytes(filename,
                                              'utf-8')).hexdigest()
            self._attachments[filename] = '/' + identifier

            # Serve the attachment using the internal server
            self._server.static(self._attachments[filename], filename)

        # Create and return the MediaAttachment object
        relative_url = self._attachments[filename]
        full_url = self._base_url + relative_url
        return messages.MediaAttachment(media_type, full_url)

    async def set_thread_settings(self, account_link_url=None,
                                  whitelisted_domains=None,
                                  get_started_payload=None,
                                  greeting_text=None,
                                  menu_buttons=None):
        '''Calls the Messenger API to set the thread settings with the given
        parameters:

        Args:
            account_link_url: The URL to use for the account linking process.
            whitelisted_domains: A list of Domain URLs to whitelist for
                                extensions.
            get_started_payload: A string payload which will be sent to the
                                 webhook when the 'Get Started' button is
                                 pressed.
            greeting_text: A string which will be displayed to new users.
            menu_buttons: A list of buttons (either URLButton or
                          PostbackButton) to add to a persistent
                          menu on the application

        Returns:
            None

        '''
        # A queue of JSON requests which will be sent one-by-one to the API.
        request_queue = []

        if account_link_url is not None:
            request_queue.append({'setting_type': 'account_linking',
                                  'account_linking_url': account_link_url})

        if whitelisted_domains is not None:
            request_queue.append({'setting_type': 'domain_whitelisting',
                                  'domain_action_type': 'add',
                                  'whitelisted_domains': whitelisted_domains})

        if get_started_payload is not None:
            request_queue.append({'setting_type': 'call_to_actions',
                                  'thread_state': 'new_thread',
                                  'call_to_actions': [{'payload':
                                                       get_started_payload}]})

        if greeting_text is not None:
            request_queue.append({'setting_type': 'greeting',
                                  'greeting': {'text': greeting_text}})

        if menu_buttons is not None:
            request_queue.append({'setting_type': 'call_to_actions',
                                  'thread_state': 'existing_thread',
                                  'call_to_actions': [button.to_json() for
                                                      button in menu_buttons]})

        # Make each request in the queue
        async with aiohttp.ClientSession(loop=self._event_loop) as session:
            for request in request_queue:
                response = await self.post(session, request,
                                           api_endpoint='thread_settings')

                # Handle errors returned by the API
                if 'result' not in response:
                    self.handle_api_error(response)

    async def get_user_information(self, user_id):
        '''Queries the Facebook API for information on the given user.

        Args:
            user_id: The integer User ID.

        Returns:
            A dictionary with the following fields: first_name, last_name,
            profile_pic, locale, timezone, gender, and is_payment_enabled.

        '''
        url = 'https://graph.facebook.com/v2.6/' \
              + str(user_id) \
              + '?access_token=' \
              + self._page_token

        # Make the GET request to the Facebook API
        async with aiohttp.ClientSession(loop=self._event_loop) as session:
                response = await self.get(session, url)

        # If the API returns an empty dictionary, raise an error
        if len(response) == 0:
            error = "The app doesn't have permission to query user with ID: " \
                    + str(user_id)
            raise MessengerAPIException(error)
        else:
            return response

    def register_handler(self, event, handler_function):
        '''Registers the given function to handle a specific event. When the event is
        triggered on the webhook, the function will be called.

        Args:
            event: The event type, like events.MESSAGE_RECEIVED

        Returns:
            None
        '''
        if event not in self._handlers:
            self._handlers[event] = []

        self._handlers[event].append(handler_function)

    def handle(self, event):
        '''A decorator which registers a function to handle the given event.

        Args:
            event: The event type, like events.MESSAGE_RECEIVED

        Returns:
            The original handler function.

        '''
        def registered_handler(handler_function):
            self.register_handler(event, handler_function)
            return handler_function

        return registered_handler
