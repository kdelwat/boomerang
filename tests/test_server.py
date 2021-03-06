"""
test_server
----------------------------------

Tests for the Messenger class.
"""

import pytest
import aiohttp
import json
import hashlib
from sanic.utils import sanic_endpoint_test
from yarl import URL

from boomerang.server import Messenger
from boomerang.messages import Message, ButtonTemplate, MediaAttachment
from boomerang.exceptions import BoomerangException, MessengerAPIException
from boomerang.events import MessageReceived, MESSAGE_RECEIVED
from boomerang.buttons import URLButton, PostbackButton


@pytest.fixture
def bot():
    '''Creates a new instance of the Messenger class.'''
    return Messenger('dummy_verify_token', 'dummy_page_token')


def test_run(bot, monkeypatch):
    '''Ensures that the run() method successfully executes.'''

    result = {}

    # To test this method, we monkeypatch the serve_multiple method of
    # the server, which will inform us when the server has successfully
    # started.
    def mock_serve(server_settings, workers):
        result['successful'] = True

    monkeypatch.setattr(bot._server, 'serve_multiple', mock_serve)

    # Run the server with two workers, in order to invoke serve_multiple()
    bot.run(processes=2)

    # Ensure the server started successfully
    assert result['successful']


def test_handle_api_error(bot):
    '''Tests the handle_api_error() method.'''
    response_json = {'error': {'message': 'Too many send requests to phone numbers',
                               'type': 'OAuthException',
                               'code': 4,
                               'error_subcode': 2018022,
                               'fbtrace_id': 'BLBaaaaaaa'}}
    exception_value = '4 (2018022): Too many send requests to phone numbers'

    with pytest.raises(MessengerAPIException) as exception:
        bot.handle_api_error(response_json)
        assert exception.value == exception_value


@pytest.mark.asyncio
async def test_post(bot, monkeypatch, event_loop):
    '''Tests the post() method.'''

    test_json = {'var1': 1, 'var2': 2}
    test_url = URL('http://www.google.com')

    # Create a ClientResponse object that will be returned as a result of the
    # mocked request.
    mock_response = aiohttp.client_reqrep.ClientResponse('post',
                                                         test_url)

    # Encode the test JSON and store it in the ClientResponse
    mock_response._content = bytes(json.dumps(test_json), encoding='ASCII')

    # Add empty headers to the ClientResponse
    mock_response.headers = aiohttp.CIMultiDictProxy(aiohttp.CIMultiDict([]))

    # A function which mocks aiohttp's ClientSession._request to return
    # the mock response.
    async def mock_request(method, url, *args, **kwargs):
        return mock_response

    monkeypatch.setattr(aiohttp.client.ClientSession, '_request', mock_request)

    # Make the post request
    async with aiohttp.ClientSession(loop=event_loop) as session:
        response = await bot.post(session, "{}")

    # Check that the response matches the desired JSON
    assert response == test_json


@pytest.mark.asyncio
async def test_get(bot, monkeypatch, event_loop):
    '''Tests the get() method.'''
    test_json = {'var1': 1, 'var2': 2}
    test_url = URL('http://www.google.com')

    # Create a ClientResponse object that will be returned as a result of the
    # mocked request.
    mock_response = aiohttp.client_reqrep.ClientResponse('get',
                                                         test_url)

    # Encode the test JSON and store it in the ClientResponse
    mock_response._content = bytes(json.dumps(test_json), encoding='ASCII')

    # Add empty headers to the ClientResponse
    mock_response.headers = aiohttp.CIMultiDictProxy(aiohttp.CIMultiDict([]))

    # A function which mocks aiohttp's ClientSession._request to return
    # the mock response.
    async def mock_request(method, url, *args, **kwargs):
        return mock_response

    monkeypatch.setattr(aiohttp.client.ClientSession, '_request', mock_request)

    # Make the get request
    async with aiohttp.ClientSession(loop=event_loop) as session:
        response = await bot.get(session, 'http://www.google.com')

    # Check that the response matches the desired JSON
    assert response == test_json


def test_is_sequence(bot):
    '''Tests the is_sequence() method.'''

    assert bot.is_sequence([])
    assert bot.is_sequence(())
    assert bot.is_sequence(['1', '2', '3'])
    assert bot.is_sequence([1, 2, 3])

    assert not bot.is_sequence('string')
    assert not bot.is_sequence(1)


@pytest.mark.asyncio
async def test_send_string(bot, monkeypatch):
    '''Tests the send() method when called with a string.'''

    result = {}

    test_string = 'dummy_string'
    test_recipient = 123

    # Mock send_message() to ensure the request is correct
    async def mock_send_message(recipient_id, message):
        result['valid'] = (message.text == test_string and recipient_id ==
                           test_recipient)

    monkeypatch.setattr(bot, 'send_message', mock_send_message)

    await bot.send(test_recipient, test_string)

    assert result['valid']


@pytest.mark.asyncio
async def test_send_message_object(bot, monkeypatch):
    '''Tests the send() method when called with a Message object.'''

    result = {}

    test_message = Message(text='dummy_text')
    test_recipient = 123

    # Mock send_message() to ensure the request is correct
    async def mock_send_message(recipient_id, message):
        result['valid'] = (message == test_message and recipient_id ==
                           test_recipient)

    monkeypatch.setattr(bot, 'send_message', mock_send_message)

    await bot.send(test_recipient, test_message)

    assert result['valid']


@pytest.mark.asyncio
async def test_send_template(bot, monkeypatch):
    '''Tests the send() method when called with a Template object.'''

    result = {}

    test_template = ButtonTemplate('dummy_description',
                                   [PostbackButton('dummy_text', 'payload')])
    test_recipient = 123

    # Mock send_message() to ensure the request is correct
    async def mock_send_message(recipient_id, message):
        result['valid'] = (message.attachment == test_template
                           and recipient_id == test_recipient)

    monkeypatch.setattr(bot, 'send_message', mock_send_message)

    await bot.send(test_recipient, test_template)

    assert result['valid']


@pytest.mark.asyncio
async def test_send_attachment(bot, monkeypatch):
    '''Tests the send() method when called with a MediaAttachment object.'''

    result = {}

    test_attachment = MediaAttachment('image', 'https://www.google.com')
    test_recipient = 123

    # Mock send_message() to ensure the request is correct
    async def mock_send_message(recipient_id, message):
        result['valid'] = (message.attachment == test_attachment
                           and recipient_id == test_recipient)

    monkeypatch.setattr(bot, 'send_message', mock_send_message)

    await bot.send(test_recipient, test_attachment)

    assert result['valid']


@pytest.mark.asyncio
async def test_send_message(bot, monkeypatch):
    '''Tests the send_message() function, checking that the desired
    message ID is returned.'''

    message = Message(text='dummy_text')
    response_json = {'recipient_id': 123,
                     'message_id': 'dummy_message_id'}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response's message ID is correctly handled
    assert await bot.send_message(123, message) == 'dummy_message_id'


@pytest.mark.asyncio
async def test_send_message_error(bot, monkeypatch):
    '''Tests the send_message() function, when the Send API returns an error.'''

    message = Message(text='dummy_text')
    response_json = {'error': {'message': 'Too many send requests to phone numbers',
                               'type': 'OAuthException',
                               'code': 4,
                               'error_subcode': 2018022,
                               'fbtrace_id': 'BLBaaaaaaa'}}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response is returned verbatim
    with pytest.raises(MessengerAPIException):
        await bot.send_message(123, message) == response_json


@pytest.mark.asyncio
async def test_send_action_error(bot, monkeypatch):
    '''Tests the send_action() function, when the Send API returns
    an error.'''

    response_json = {'error': {'message': 'Too many send requests to phone numbers',
                               'type': 'OAuthException',
                               'code': 4,
                               'error_subcode': 2018022,
                               'fbtrace_id': 'BLBaaaaaaa'}}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    with pytest.raises(MessengerAPIException):
        await bot.send_action(123, 'typing_on')


@pytest.mark.asyncio
async def test_send_action_invalid(bot):
    '''Tests the send_action() function when called with an invalid
    action.'''

    with pytest.raises(BoomerangException):
        await bot.send_action(123, 'invalid_action')


@pytest.mark.asyncio
async def test_send_action(bot, monkeypatch):
    '''Tests the send_action() function, checking that the desired
    message ID is returned.'''

    response_json = {'recipient_id': 123}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response is correctly handled
    assert await bot.send_action(123, 'typing_on')


@pytest.mark.asyncio
async def test_acknowledge(bot, monkeypatch):
    '''Tests the acknowledge() function, ensuring it calls send_action
    with the appropriate arguments.'''
    result = {}

    # Create a MessageReceived event
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}

    message_received_event = MessageReceived.from_json(123, 1234567890,
                                                       json_data)

    # Mock the send_action method to record all actions sent in the result
    # dictionary
    async def mock_send_action(recipient_id, action):
        if recipient_id == 123:
            result[action] = True

    monkeypatch.setattr(bot, 'send_action', mock_send_action)

    # Ensure that all required actions were sent
    await bot.acknowledge(message_received_event)
    assert result['mark_seen'] and result['typing_on']


@pytest.mark.asyncio
async def test_respond_to(bot, monkeypatch):
    result = {}

    # Create a MessageReceived event
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}

    message_received_event = MessageReceived.from_json(123, 1234567890,
                                                       json_data)

    # Create a response Message
    response = Message(text='dummy_text')

    # Mock the send_message() function to record arguments it receives
    async def mock_send_message(recipient_id, message):
        result['recipient_id'] = recipient_id
        result['message'] = message

    monkeypatch.setattr(bot, 'send_message', mock_send_message)

    # Ensure respond_to calls send() with the appropriate arguments
    await bot.respond_to(message_received_event, response)
    assert result['recipient_id'] == 123
    assert result['message'] == response


@pytest.mark.asyncio
async def test_host_attachment(bot, monkeypatch):
    '''Tests the host_attachment() method by ensuring static hosting
    is correctly initialised and the correct MediaAttachment is returned.'''

    # Set a counter for the number of times static() is called.
    result = {'called': 0}

    # Generate the required URL
    relative_url = '/' + hashlib.sha256(bytes('image.png', 'utf-8')).hexdigest()

    # Set the base_url of the Messenger instance, which would normally be
    # set when run() is called.
    bot._base_url = 'http://base.com'

    # Mock the static() function to record arguments it receives
    def mock_static(url, filename):
        result['URL'] = url
        result['filename'] = filename

        # Increment the number of times static() is called
        # (it should only be once)
        result['called'] += 1

    monkeypatch.setattr(bot._server, 'static', mock_static)

    # Host a new attachment
    attachment = await bot.host_attachment('image', 'image.png')

    assert attachment.url == 'http://base.com' + relative_url
    assert result['URL'] == relative_url
    assert result['filename'] == 'image.png'

    # Re-host the same attachment, checking that it is not re-served.
    attachment = await bot.host_attachment('image', 'image.png')

    assert attachment.url == 'http://base.com' + relative_url
    assert result['URL'] == relative_url
    assert result['filename'] == 'image.png'
    assert result['called'] == 1


@pytest.mark.asyncio
async def test_host_attachment_no_base_url(bot):
    '''Tests that the host_attachment() method raises an error when
    base_url hasn't been set.'''
    bot._base_url = None
    with pytest.raises(BoomerangException):
        await bot.host_attachment('image', 'image.png')

@pytest.mark.asyncio
async def test_set_thread_settings(bot, monkeypatch):
    '''Tests the set_thread_settings method by ensuring it calls post()
    with the correct parameters.'''

    # The result dictionary holds a list of booleans
    result = {'success': []}

    # Mock the post() function to validate arguments it receives
    async def mock_post(session, request, api_endpoint='messages'):

        # This really ugly list contains the correct request JSON
        valid = [{'account_linking_url': 'https://cadelwatson.com',
                  'setting_type': 'account_linking'},
                 {'domain_action_type': 'add',
                  'setting_type': 'domain_whitelisting',
                  'whitelisted_domains': ['https://google.com']},
                 {'call_to_actions': [{'payload': 'payload'}],
                  'setting_type': 'call_to_actions',
                  'thread_state': 'new_thread'},
                 {'greeting': {'text': 'hi there'}, 'setting_type': 'greeting'},
                 {'call_to_actions': [{'title': 'Google',
                                       'type': 'web_url',
                                       'url': 'http://www.google.com'},
                                      {'payload': 'mmmmmm',
                                       'title': 'Hit me',
                                       'type': 'postback'}],
                  'setting_type': 'call_to_actions',
                  'thread_state': 'existing_thread'}]

        # Check that the request given to post() is valid
        if request in valid and api_endpoint == 'thread_settings':
            result['success'].append(True)
        else:
            result['success'].append(False)

        # Return a dummy response
        return {'result': 'success'}

    monkeypatch.setattr(bot, 'post', mock_post)

    # Create a thread settings request
    button_list = [URLButton('Google', 'http://www.google.com'),
                   PostbackButton('Hit me', 'mmmmmm')]

    await bot.set_thread_settings(menu_buttons=button_list,
                                  account_link_url='https://cadelwatson.com',
                                  whitelisted_domains=['https://google.com'],
                                  get_started_payload='payload',
                                  greeting_text='hi there')

    # Ensure that all post() requests were valid
    assert all(result['success'])


@pytest.mark.asyncio
async def test_set_thread_settings_error(bot, monkeypatch):
    '''Tests the set_thread_settings method when one of the API
    calls returns an error.'''

    # Mock the post() function to return an error
    async def mock_post(session, request, api_endpoint='messages'):
        return {'error': {'message': 'Too many send requests to phone numbers',
                          'type': 'OAuthException',
                          'code': 4,
                          'error_subcode': 2018022,
                          'fbtrace_id': 'BLBaaaaaaa'}}

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure that an exception is raised when an error is returned by the API
    with pytest.raises(MessengerAPIException):
        await bot.set_thread_settings(account_link_url='https://google.com')


@pytest.mark.asyncio
async def test_get_user_information(bot, monkeypatch):
    '''Tests the get_user_information() method.'''
    result = {}

    access_token = bot._page_token
    required_url = 'https://graph.facebook.com/v2.6/12345?access_token=' \
                   + access_token

    mock_response = {'profile_pic': 'https://www.google.com',
                     'gender': 'male',
                     'locale': 'en_GB',
                     'first_name': 'Busta',
                     'last_name': 'Rhymes',
                     'timezone': 0}

    # Mock the get() function to validate arguments it receives
    async def mock_get(session, url):
        # Check that the URL given is valid
        if url == required_url:
            result['success'] = True
        else:
            result['success'] = False

        # Return a dummy response
        return mock_response

    monkeypatch.setattr(bot, 'get', mock_get)

    # Ensure the correct response is returned
    assert await bot.get_user_information(12345) == mock_response

    # Ensure the correct URL was created
    assert result['success']


@pytest.mark.asyncio
async def test_get_user_information_permission_denied(bot, monkeypatch):
    '''Tests the get_user_information() method when permission to the user is
    denied.'''

    # Mock the get() function to return an empty response
    async def mock_get(session, url):
        return {}

    monkeypatch.setattr(bot, 'get', mock_get)

    with pytest.raises(MessengerAPIException):
        await bot.get_user_information(12345)


def test_valid_register(bot):
    '''Tests valid registration request by the Messenger Platform.'''
    valid_request = {'hub.mode': 'subscribe',
                     'hub.verify_token': 'dummy_verify_token',
                     'hub.challenge': 'dummy_challenge'}

    response = sanic_endpoint_test(bot._server,
                                   gather_request=False,
                                   uri='/webhook',
                                   params=valid_request)

    assert response.text == valid_request['hub.challenge']
    assert response.status == 200


def test_invalid_register(bot):
    '''Tests the response when verify_tokens do not match.'''
    invalid_request = {'hub.mode': 'subscribe',
                       'hub.verify_token': 'wrong_verify_token',
                       'hub.challenge': 'dummy_challenge'}

    response = sanic_endpoint_test(bot._server,
                                   gather_request=False,
                                   uri='/webhook',
                                   params=invalid_request)

    # Ensure the server doesn't provide the correct challenge anyway
    assert response.text != invalid_request['hub.challenge']

    # Check that the server replied that access was forbidden
    assert response.status == 403


@pytest.mark.asyncio
async def test_handle_event(bot, monkeypatch):
    '''Tests that the handle_event method calls the appropriate handler
    functions.'''

    result = {}

    # A mock handler function which records when it is called
    async def mock_handle_received(message):
        result['called'] = True

    # Monkeypatch the bot's handlers to call the mock handler for message
    # received event
    mock_handlers = {MESSAGE_RECEIVED: [mock_handle_received]}
    monkeypatch.setattr(bot, '_handlers', mock_handlers)

    # Handle a MessageReceived event
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}

    message_received_event = MessageReceived.from_json(123, 1234567890,
                                                       json_data)

    await bot.handle_event(MESSAGE_RECEIVED, message_received_event)

    # Ensure the handler function was called.
    assert result['called']


def test_handler_registration(bot):
    '''Tests the handle decorator and register_handle function.'''

    @bot.handle(MESSAGE_RECEIVED)
    async def mock_handler(message):
        pass

    assert bot._handlers[MESSAGE_RECEIVED] == [mock_handler]


@pytest.mark.asyncio
async def test_handler_return(bot, monkeypatch):
    '''Tests that handler functions can return objects, which are sent.'''

    @bot.handle(MESSAGE_RECEIVED)
    async def mock_handler(message):
        return 'dummy_text'

    result = {}

    # Mock send() to ensure the response is correct
    async def mock_send(recipient_id, item):
        result['valid'] = (item == 'dummy_text' and recipient_id == 123)

    monkeypatch.setattr(bot, 'send', mock_send)

    # Simulate a MessageReceived event
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}
    message_received_event = MessageReceived.from_json(123, 1234567890,
                                                       json_data)
    await bot.handle_event(MESSAGE_RECEIVED, message_received_event)

    assert result['valid']


@pytest.mark.asyncio
async def test_handler_return_sequence(bot, monkeypatch):
    '''Tests that handler functions can return a sequnce of objects, which are
    each sent.'''

    @bot.handle(MESSAGE_RECEIVED)
    async def mock_handler(message):
        return ['dummy_text'] * 5

    result = {'called': 0}

    # Mock send() to count number of valid calls
    async def mock_send(recipient_id, item):
        if item == 'dummy_text' and recipient_id == 123:
            result['called'] += 1

    monkeypatch.setattr(bot, 'send', mock_send)

    # Simulate a MessageReceived event
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}
    message_received_event = MessageReceived.from_json(123, 1234567890,
                                                       json_data)
    await bot.handle_event(MESSAGE_RECEIVED, message_received_event)

    # Ensure that send() was called one time for each response in the returned
    # list
    assert result['called'] == 5


def message_handled_ok(server, message_type, message_content):
    '''Makes a POST request to the server, simulating the given message being
    sent, and ensure the server responds with a 200 OK status.

    Args:
        server: A Sanic server to test against.
        message_type: A string of the type of message, given as the Messenger
                      API string for the type.
        message_content: A dict representing the JSON message to be tested.

    Returns:
        True if a 200 OK response is received, otherwise False.

    '''

    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{message_type: message_content,
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json_string = json.dumps(message)

    request, response = sanic_endpoint_test(server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json_string)

    return response.status == 200


def test_message_received(bot):
    '''Ensure the server responds with a 200 status to a message received event
    sent by the API.'''
    message = {'mid': 'mid.1482375186449:88d829fb30',
               'seq': 426185,
               'text': 'ping'}
    assert message_handled_ok(bot._server, 'message', message)


def test_message_delivered(bot):
    '''Ensure the server responds with a 200 status to a message delivered event
    sent by the API.'''
    message = {'mids': ['mid.1458668856218:ed81099e15d3f4f233',
                        'mid.1458668856218:ed81099e15d3f4f234'],
               'watermark': 1111111111,
               'seq': 30}

    assert message_handled_ok(bot._server, 'delivery', message)


def test_message_read(bot):
    '''Ensure the server responds with a 200 status to a message read event
    sent by the API.'''
    message = {'watermark': 1111111111,
               'seq': 30}

    assert message_handled_ok(bot._server, 'read', message)


def test_postback(bot):
    '''Ensure the server responds with a 200 status to a postback event
    sent by the API.'''
    message = {'payload': 'dummy_payload'}

    assert message_handled_ok(bot._server, 'postback', message)


def test_postback_with_referral(bot):
    '''Ensure the server responds with a 200 status to a postback event
    sent by the API, when the postback contains a referral.'''
    message = {'payload': 'dummy_payload',
               'referral': {'ref': 'dummy_referral_data',
                            'source': 'SHORTLINK',
                            'type': 'OPEN_THREAD'}}

    assert message_handled_ok(bot._server, 'postback', message)


def test_referral(bot):
    '''Ensure the server responds with a 200 status to a referral event
    sent by the API.'''
    message = {'ref': 'dummy_referral_data',
               'source': 'SHORTLINK',
               'type': 'OPEN_THREAD'}

    assert message_handled_ok(bot._server, 'referral', message)


def test_optin(bot):
    '''Ensure the server responds with a 200 status to a plugin opt in event
    sent by the API.'''
    message = {'ref': 'dummy_data'}

    assert message_handled_ok(bot._server, 'optin', message)


def test_account_linking(bot):
    '''Ensure the server responds with a 200 status to an account linking event
    sent by the API.'''
    message = {'status': 'linked',
               'authorization_code': 'dummy_authorization'}

    assert message_handled_ok(bot._server, 'account_linking', message)
