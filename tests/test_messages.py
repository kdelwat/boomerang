"""
test_messages
----------------------------------

Tests for classes in the messages module.
"""

from messengerplatform import messages


def test_message_received():
    '''Tests the to_json and from_json functionality of the basic Message class.

    '''
    json_data = {'mid': 'mid.1482375186449:88d829fb30',
                 'seq': 426185,
                 'text': 'ping'}
    user_id = 12345
    timestamp = 1234567890

    message_object = messages.Message.from_json(user_id, timestamp, json_data)

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

    message_object = messages.Message.from_json(user_id, timestamp, json_data)

    assert len(message_object.attachments) == 2
    assert isinstance(message_object.attachments[0],
                      messages.MediaAttachment)
    assert isinstance(message_object.attachments[1],
                      messages.LocationAttachment)


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

    message_object = messages.Message.from_json(user_id, timestamp, json_data)

    assert isinstance(message_object.quick_reply, messages.QuickReply)
    assert message_object.quick_reply.payload == 'dummy_payload'


def test_attachments():
    '''Tests the to_json and from_json functionality of the attachment classes.

    '''
    media_json_data = {'payload': {'url': 'http://www.google.com'},
                       'type': 'image'}

    attachment_object = messages.MediaAttachment.from_json(media_json_data)
    assert attachment_object.media_type == 'image'
    assert attachment_object.url == 'http://www.google.com'

    location_json_data = {'title': "Someones's Location",
                          'type': 'location',
                          'url': 'dummy_url',
                          'payload': {'coordinates': {'long': 38.8976763,
                                                      'lat': -77.0387185}}}

    location_object = messages.LocationAttachment.from_json(location_json_data)
    assert location_object.latitude == -77.0387185
    assert location_object.longitude == 38.8976763


def test_quickreply():
    '''Tests the from_json functionality of the QuickReply class.

    '''
    json_data = {'payload': 'dummy_payload'}

    quickreply_object = messages.QuickReply.from_json(json_data)
    assert quickreply_object.payload == 'dummy_payload'
