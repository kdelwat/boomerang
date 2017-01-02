"""
test_messages
----------------------------------

Tests for classes in the messages module.
"""

import pytest

from boomerang import messages, exceptions, buttons


def test_invalid_message():
    '''Ensures that Message objects require either a text message or Attachment
    when being initialised.'''
    with pytest.raises(exceptions.BoomerangException):
        messages.Message()


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


def test_button_text_too_long():
    '''Ensures that Buttons raise an error when their text is too long.'''

    with pytest.raises(exceptions.BoomerangException):
        buttons.URLButton('This text is greater than 20',
                                       'http://www.google.com')


def test_button_template_json():
    '''Tests the to_json() functionality of the ButtonTemplate class.'''

    url_button = buttons.URLButton('Google', 'http://www.google.com')
    postback_button = buttons.PostbackButton('Postback', 'dummy_payload')
    call_button = buttons.CallButton('Call', '+15105551234')
    attachment = messages.ButtonTemplate('Select a URL', [url_button,
                                                          postback_button,
                                                          call_button])
    message = messages.Message(attachment=attachment)

    payload_json = {'template_type': 'button',
                    'text': 'Select a URL',
                    'buttons': [{'type': 'web_url',
                                 'url': 'http://www.google.com',
                                 'title': 'Google'},
                                {'type': 'postback',
                                 'payload': 'dummy_payload',
                                 'title': 'Postback'},
                                {'type': 'phone_number',
                                 'payload': '+15105551234',
                                 'title': 'Call'}]}

    message_json = {'attachment': {'type': 'template',
                                   'payload': payload_json}}

    assert message.to_json() == message_json


def test_button_template_json_share():
    '''Tests the to_json() functionality of the ButtonTemplate class,
    when a ShareButton is present.'''

    share_button = buttons.ShareButton()
    attachment = messages.ButtonTemplate('Select a URL', [share_button])
    message = messages.Message(attachment=attachment)

    payload_json = {'template_type': 'button',
                    'text': 'Select a URL',
                    'buttons': [{'type': 'element_share'}]}

    message_json = {'attachment': {'type': 'template',
                                   'payload': payload_json}}

    assert message.to_json() == message_json


def test_quick_reply():
    '''Tests the initialisation of the QuickReply class.'''

    # Ensure the QuickReply button_type can only be 'text' or 'location'
    with pytest.raises(exceptions.BoomerangException):
        buttons.QuickReply('image')

    # Ensure error is raised on missing text arguments
    with pytest.raises(exceptions.BoomerangException):
        buttons.QuickReply('text', text='dummy_text')

    with pytest.raises(exceptions.BoomerangException):
        buttons.QuickReply('text', payload='dummy_payload')

    # Ensure no other attributes are given when creating a location
    # QuickReply
    with pytest.raises(exceptions.BoomerangException):
        buttons.QuickReply('location', text='dummy_text')


def test_quick_reply_json():
    '''Tests the to_json() functionality of the QuickReply class.'''

    text_button = buttons.QuickReply('text', text='Button',
                                     payload='button_pressed',
                                     image_url='http://www.google.com')
    location_button = buttons.QuickReply('location')

    message = messages.Message(text='Choose a button',
                               quick_replies=[text_button,
                                              location_button])

    message_json = {'text': 'Choose a button',
                    'quick_replies': [{'content_type': 'text',
                                       'title': 'Button',
                                       'payload': 'button_pressed',
                                       'image_url': 'http://www.google.com'},
                                      {'content_type': 'location'}]}

    assert message.to_json() == message_json


def test_invalid_list_template():
    '''Tests the error-checking in the ListTemplate class.'''
    url_button = buttons.URLButton('Google', 'http://www.google.com')
    default_action = messages.DefaultAction('https://i.imgur.com/MBUyt0n.png')
    element = messages.Element('Element', sub_title='Element subtitle',
                               image_url='https://i.imgur.com/MBUyt0n.png',
                               default_action=default_action,
                               buttons=[url_button])

    # Between 2 and 4 elements must be provided
    with pytest.raises(exceptions.BoomerangException):
        list_template = messages.ListTemplate([])

    with pytest.raises(exceptions.BoomerangException):
        list_template = messages.ListTemplate([element, element, element,
                                               element, element])

    # Ensure that the first element of a ListTemplate in non-compact form
    # contains an image
    imageless_element = messages.Element('Element',
                                         default_action=default_action,
                                         buttons=[url_button])

    with pytest.raises(exceptions.BoomerangException):
        messages.ListTemplate([imageless_element, element],
                              compact=False)


def test_list_template_json():
    '''Tests the to_json() functionality of the ListTemplate class.'''

    url_button = buttons.URLButton('Google', 'http://www.google.com')
    default_action = messages.DefaultAction('https://i.imgur.com/MBUyt0n.png')
    element = messages.Element('Element', sub_title='Element subtitle',
                               image_url='https://i.imgur.com/MBUyt0n.png',
                               default_action=default_action,
                               buttons=[url_button])

    attachment = messages.ListTemplate([element, element],
                                       button=url_button)

    message = messages.Message(attachment=attachment)

    element_json = {'title': 'Element',
                    'subtitle': 'Element subtitle',
                    'image_url': 'https://i.imgur.com/MBUyt0n.png',
                    'default_action': {'type': 'web_url',
                                       'url': 'https://i.imgur.com/MBUyt0n.png'},
                    'buttons': [{'type': 'web_url',
                                 'title': 'Google',
                                 'url': 'http://www.google.com'}]}

    payload_json = {'template_type': 'list',
                    'elements': [element_json, element_json],
                    'buttons': [{'type': 'web_url',
                                 'url': 'http://www.google.com',
                                 'title': 'Google'}],
                    'top_element_style': 'compact'}

    message_json = {'attachment': {'type': 'template',
                                   'payload': payload_json}}

    assert message.to_json() == message_json


def test_generic_template_element_limit():
    '''Ensures that GenericTemplate raises an exception when the number
    of elements is greater than 10.'''
    default_action = messages.DefaultAction('https://i.imgur.com/MBUyt0n.png')

    element = messages.Element('Element', sub_title='Element subtitle',
                               image_url='https://i.imgur.com/MBUyt0n.png',
                               default_action=default_action)

    with pytest.raises(exceptions.BoomerangException):
        messages.GenericTemplate([element] * 11)


def test_generic_template_json():
    '''Tests the to_json() functionality of the GenericTemplate class.'''

    url_button = buttons.URLButton('Google', 'http://www.google.com')
    postback_button = buttons.PostbackButton('Postback', 'dummy_payload')
    default_action = messages.DefaultAction('https://i.imgur.com/MBUyt0n.png')

    element = messages.Element('Element', sub_title='Element subtitle',
                               image_url='https://i.imgur.com/MBUyt0n.png',
                               default_action=default_action,
                               buttons=[url_button, postback_button])

    attachment = messages.GenericTemplate([element, element])

    message = messages.Message(attachment=attachment)

    element_json = {'title': 'Element',
                    'subtitle': 'Element subtitle',
                    'image_url': 'https://i.imgur.com/MBUyt0n.png',
                    'default_action': {'type': 'web_url',
                                       'url': 'https://i.imgur.com/MBUyt0n.png'},
                    'buttons': [{'type': 'web_url',
                                 'title': 'Google',
                                 'url': 'http://www.google.com'},
                                {'type': 'postback',
                                 'payload': 'dummy_payload',
                                 'title': 'Postback'}]}

    payload_json = {'template_type': 'generic',
                    'elements': [element_json, element_json]}

    message_json = {'attachment': {'type': 'template',
                                   'payload': payload_json}}

    assert message.to_json() == message_json
