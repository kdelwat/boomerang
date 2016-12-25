"""
test_server
----------------------------------

Tests for the Messenger class.
"""

import pytest
import aiohttp
import json
from sanic.utils import sanic_endpoint_test

from boomerang.server import Messenger


@pytest.fixture
def bot():
    '''Creates a new instance of the Messenger class.'''
    return Messenger('dummy_verify_token', 'dummy_page_token')


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
