"""
test_events
----------------------------------

Tests for classes in the events module.
"""

from boomerang import events


def test_message_received():
    '''Tests the to_json and from_json functionality of the basic Message class.

    '''
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}
    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageReceived.from_json(user_id, timestamp,
                                                      json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.message_id == json_data['mid']
    assert message_object.sequence_position == json_data['seq']
    assert message_object.text == json_data['text']


def test_message_received_with_attachments():
    '''Tests the to_json and from_json functionality of the basic Message class,
    with attachments included.

    '''
    image_attachment = {'payload': {'url': 'http://www.google.com'},
                        'type': 'image'}
    location_attachment = {'title': "Someones's Location",
                           'type': 'location',
                           'url': 'dummy_url',
                           'payload': {'coordinates': {'long': 38.8976763,
                                                       'lat': -77.0387185}}}
    json_data = {'attachments': [image_attachment, location_attachment],
                 'mid': 'mid.1482375360960:63e41d7f60',
                 'seq': 426187}
    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageReceived.from_json(user_id, timestamp,
                                                      json_data)

    assert len(message_object.attachments) == 2
    assert isinstance(message_object.attachments[0],
                      events.MediaAttachment)
    assert isinstance(message_object.attachments[1],
                      events.LocationAttachment)


def test_message_received_with_quickreply():
    '''Tests the to_json and from_json functionality of the basic Message class,
    with a quick reply included.

    '''
    json_data = {'mid': 'mid.1457764197618:41d102a3e1ae206a38',
                 'seq': 12345,
                 'text': 'dummy_text',
                 'quick_reply': {'payload': 'dummy_payload'}}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageReceived.from_json(user_id, timestamp,
                                                      json_data)

    assert isinstance(message_object.quick_reply, events.QuickReply)
    assert message_object.quick_reply.payload == 'dummy_payload'


def test_message_delivered():
    '''Tests the to_json functionality of the MessageDelivered class.

    '''
    json_data = {'mids': ['mid.1458668856218:ed81099e15d3f4f233',
                          'mid.1458668856218:ed81099e15d3f4f234'],
                 'watermark': 1111111111,
                 'seq': 30}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageDelivered.from_json(user_id, timestamp,
                                                       json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.watermark == json_data['watermark']
    assert message_object.sequence_position == json_data['seq']

    assert isinstance(message_object.message_ids, list)
    assert message_object.message_ids[0] == 'mid.1458668856218:ed81099e15d3f4f233'


def test_message_read():
    '''Tests the to_json functionality of the MessageRead class.

    '''
    json_data = {'watermark': 1111111111,
                 'seq': 30}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageRead.from_json(user_id, timestamp,
                                                  json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.watermark == json_data['watermark']
    assert message_object.sequence_position == json_data['seq']


def test_postback():
    '''Tests the to_json functionality of the Postback class.

    '''
    json_data = {'payload': 'dummy_payload'}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.Postback.from_json(user_id, timestamp, json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.payload == 'dummy_payload'
    assert message_object.referral is None


def test_postback_with_referral():
    '''Tests the to_json functionality of the Postback class, when a referral is
    included.

    '''
    json_data = {'payload': 'dummy_payload',
                 'referral': {'ref': 'dummy_referral_data',
                              'source': 'SHORTLINK',
                              'type': 'OPEN_THREAD'}}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.Postback.from_json(user_id, timestamp, json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.payload == 'dummy_payload'

    assert isinstance(message_object.referral, events.Referral)
    assert message_object.referral.data == 'dummy_referral_data'


def test_referral():
    '''Tests the to_json functionality of the Referral class.

    '''
    json_data = {'ref': 'dummy_referral_data',
                 'source': 'SHORTLINK',
                 'type': 'OPEN_THREAD'}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.Referral.from_json(user_id, timestamp, json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.data == 'dummy_referral_data'


def test_optin():
    '''Tests the to_json functionality of the OptIn class.

    '''
    json_data = {'ref': 'dummy_data'}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.OptIn.from_json(user_id, timestamp, json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.data == 'dummy_data'


def test_account_unlinked():
    '''Tests the to_json functionality of the AccountLink class, when
    the account is being unlinked.

    '''

    json_data = {'status': 'unlinked'}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.AccountLink.from_json(user_id, timestamp,
                                                  json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.status == 'unlinked'
    assert message_object.authorization_code is None


def test_account_linked():
    '''Tests the to_json functionality of the AccountLink class, when
    the account is being linked.

    '''

    json_data = {'status': 'linked',
                 'authorization_code': 'dummy_authorization'}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.AccountLink.from_json(user_id, timestamp,
                                                  json_data)

    assert message_object.user_id == user_id
    assert message_object.timestamp == timestamp
    assert message_object.status == 'linked'
    assert message_object.authorization_code == 'dummy_authorization'


def test_message_delivered_with_no_message_ids():
    '''Tests the to_json functionality of the MessageDelivered class,
    when the array of message IDs is missing.

    '''
    json_data = {'watermark': 1111111111,
                 'seq': 30}

    user_id = 12345
    timestamp = 1234567890

    message_object = events.MessageDelivered.from_json(user_id, timestamp,
                                                       json_data)

    assert isinstance(message_object.message_ids, list)
    assert len(message_object.message_ids) == 0


def test_attachments():
    '''Tests the to_json and from_json functionality of the attachment classes.

    '''
    media_json_data = {'payload': {'url': 'http://www.google.com'},
                       'type': 'image'}

    attachment_object = events.MediaAttachment.from_json(media_json_data)
    assert attachment_object.media_type == 'image'
    assert attachment_object.url == 'http://www.google.com'

    location_json_data = {'title': "Someones's Location",
                          'type': 'location',
                          'url': 'dummy_url',
                          'payload': {'coordinates': {'long': 38.8976763,
                                                      'lat': -77.0387185}}}

    location_object = events.LocationAttachment.from_json(location_json_data)
    assert location_object.latitude == -77.0387185
    assert location_object.longitude == 38.8976763


def test_quickreply():
    '''Tests the from_json functionality of the QuickReply class.

    '''
    json_data = {'payload': 'dummy_payload'}

    quickreply_object = events.QuickReply.from_json(json_data)
    assert quickreply_object.payload == 'dummy_payload'
