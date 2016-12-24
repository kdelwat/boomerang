"""
test_messenger
----------------------------------

Tests for the Messenger class.
"""

import pytest
import aiohttp
import json
from sanic.utils import sanic_endpoint_test

from boomerang import Messenger


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


def test_message_received(bot):
    '''Makes a POST request simulating a message to the bot, checking that the
    bot responds with the appropriate status.'''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'message': {'mid': 'mid.1482375186449:88d829fb30',
                                                     'seq': 426185,
                                                     'text': 'ping'},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200


def test_message_delivered(bot):
    '''Makes a POST request simulating a message delivered event to the bot,
    checking that the bot responds with the appropriate status.'''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'delivery': {'mids': ['mid.1458668856218:ed81099e15d3f4f233',
                                                               'mid.1458668856218:ed81099e15d3f4f234'],
                                                      'watermark': 1111111111,
                                                      'seq': 30},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200


def test_message_read(bot):
    '''Makes a POST request simulating a message read event to the bot,
    checking that the bot responds with the appropriate status.'''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'read': {'watermark': 1111111111,
                                                  'seq': 30},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200


def test_postback(bot):
    '''Makes a POST request simulating a postback event to the bot,
    checking that the bot responds with the appropriate status.'''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'postback': {'payload': 'dummy_payload'},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200


def test_postback_with_referral(bot):
    '''Makes a POST request simulating a postback event to the bot, where a
    referral is included, checking that the bot responds with the appropriate
    status.

    '''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'postback': {'payload': 'dummy_payload',
                                                      'referral': {'ref': 'dummy_referral_data',
                                                                   'source': 'SHORTLINK',
                                                                   'type': 'OPEN_THREAD'}},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200


def test_referral(bot):
    '''Makes a POST request simulating a referral event to the bot,
    checking that the bot responds with the appropriate status.'''
    message = {'entry': [{'id': '233231370449158',
                          'messaging': [{'referral': {'ref': 'dummy_referral_data',
                                                      'source': 'SHORTLINK',
                                                      'type': 'OPEN_THREAD'},
                                         'recipient': {'id': '233231370449158'},
                                         'sender': {'id': '1297601746979209'},
                                         'timestamp': 1482375186449}],
                          'time': 1482375186497}],
               'object': 'page'}

    message_json = json.dumps(message)

    request, response = sanic_endpoint_test(bot._server,
                                            method='post',
                                            uri='/webhook',
                                            data=message_json)
    assert response.status == 200
