"""
test_messages
----------------------------------

Tests for classes in the messages module.
"""

import pytest

from boomerang import messages, exceptions


def test_invalid_message():
    '''Ensures that Message objects require either a text message or Attachment
    when being initialised.'''
    with pytest.raises(exceptions.BoomerangException):
        message = messages.Message()


def test_text_message_json():
    '''Tests the to_json() functionality of the Message class, when it contains
    a text message.'''
    message = messages.Message(text='dummy_text')

    required_json = {'text': 'dummy_text'}

    assert message.to_json() == required_json


def test_media_attachment_json():
    '''Tests the to_json() functionality of the MediaAttachment class.'''

    attachment = messages.MediaAttachment('image', 'http://www.google.com')
    attachment_json = {'type': 'image',
                       'payload': {'url': 'http://www.google.com'}}
    message = messages.Message(attachment=attachment)

    assert attachment.to_json() == attachment_json
    assert message.to_json() == {'attachment': attachment_json}
