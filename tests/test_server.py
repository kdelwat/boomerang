"""
test_server
----------------------------------

Tests for the Messenger class.
"""

import pytest
import aiohttp
import json
from sanic.utils import sanic_endpoint_test
from yarl import URL

from boomerang.server import Messenger
from boomerang.messages import Message
from boomerang.exceptions import BoomerangException
from boomerang.events import MessageReceived


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
async def test_send(bot, monkeypatch):
    '''Tests the send() function, checking that the desired
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
    assert await bot.send(123, message) == 'dummy_message_id'


@pytest.mark.asyncio
async def test_send_error(bot, monkeypatch):
    '''Tests the send() function, when the Send API returns an error.'''

    message = Message(text='dummy_text')
    response_json = {'error': 'dummy_error'}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response is returned verbatim
    assert await bot.send(123, message) == response_json


@pytest.mark.asyncio
async def test_send_action_error(bot, monkeypatch):
    '''Tests the send_action() function, when the Send API returns
    an error.'''

    response_json = {'error': 'dummy_error'}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response is returned verbatim
    assert await bot.send_action(123, 'typing_on') == response_json


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

    response_json = {'recipient_id': 123,
                     'message_id': 'dummy_message_id'}

    # Monkeypatch the Messenger.post method to return the desired
    # JSON
    async def mock_post(session, json_string):
        return response_json

    monkeypatch.setattr(bot, 'post', mock_post)

    # Ensure the response's message ID is correctly handled
    assert await bot.send_action(123, 'typing_on') == 'dummy_message_id'


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

    # Mock the send() function to record arguments it receives
    async def mock_send(recipient_id, message):
        result['recipient_id'] = recipient_id
        result['message'] = message

    monkeypatch.setattr(bot, 'send', mock_send)

    # Ensure respond_to calls send() with the appropriate arguments
    await bot.respond_to(message_received_event, response)
    assert result['recipient_id'] == 123
    assert result['message'] == response


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
