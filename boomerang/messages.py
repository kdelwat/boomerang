import abc

from .exceptions import BoomerangException


class Message():
    '''A class for messages to be sent to the Send API.

    Attributes:
        text: A string representing the text of the message.
        attachment: An Attachment object.
        quick_replies: A list of QuickReply objects.
        metadata: A string set by the developer that will be returned
                  to the webhook.
    '''

    def __init__(self, text=None, attachment=None, quick_replies=[],
                 metadata=None):

        # Ensure that either a text message or attachment is present.
        if text is None and attachment is None:
            error = 'Message objects require either text or an attachment'
            raise BoomerangException(error)

        self.text = text
        self.attachment = attachment
        self.quick_replies = quick_replies
        self.metadata = metadata

    def to_json(self):
        '''Converts the message to JSON.

        Returns:
            A dictionary holding the JSON representation of a message, which
            can be passed to the send() function.

        '''
        json = {}

        if self.text is not None:
            json['text'] = self.text

        if self.attachment is not None:
            json['attachment'] = self.attachment.to_json()

        if len(self.quick_replies) > 0:
            json['quick_replies'] = [quick_reply.to_json() for quick_reply in
                                     self.quick_replies]

        return json


class MediaAttachment:
    '''A class holding media attachments.

    Attributes:
        media_type: The type of the attachment. Can be one of
                    'image', 'audio', 'video', or 'file'.
        url: The url of the media as a string.

    '''

    def __init__(self, media_type, url):
        self.media_type = media_type
        self.url = url

    @classmethod
    def from_json(cls, json):
        '''Builds a MediaAttachment object from JSON provided by the API.

        Args:
            json: A dict containing the JSON representation that is converted
                  into the MediaAttachment object.

        Returns:
            A MediaAttachment object.

        '''
        return cls(json['type'], json['payload']['url'])

    def to_json(self):
        '''Converts the attachment to JSON.

        Returns:
            A dictionary holding the JSON representation of a media
            attachment.

        '''

        json = {'type': self.media_type,
                'payload': {'url': self.url}}

        return json


class LocationAttachment:
    '''A class holding location attachments.

    Attributes:
        latitude: A float of the latitude of the location.
        longitude: A float of the longitude of the location.

    '''

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_json(cls, json):
        '''Builds a LocationAttachment object from JSON provided by the API.

        Args:
            json: A dict containing the JSON representation that is converted
                  into the LocationAttachment object.

        Returns:
            A LocationAttachment object.

        '''
        return cls(json['payload']['coordinates']['lat'],
                   json['payload']['coordinates']['long'])


class Template(metaclass=abc.ABCMeta):
    '''The abstract base class for all template types.'''

    @abc.abstractmethod
    def to_json(self, payload):
        '''Implements the to_json() method for all template types.

        This method provides the JSON representation common to all templates,
        namely the 'type' and 'payload' attributes. Each subclass must call
        this method using super, and provide its own JSON representation of the
        payload.

        Args:
            payload: A dictionary JSON representation of the template's payload.

        Returns:
            A dictionary containing the complete JSON representation of
            the template.
        '''
        return {'type': 'template',
                'payload': payload}


class ButtonTemplate(Template):
    '''A class representing a button template.

    Attributes:
        text: The text of the message.
        buttons: A list of Button objects to include.

    '''
    def __init__(self, text, buttons):
        self.text = text
        self.buttons = buttons

    def to_json(self):
        '''Converts the template to JSON.

        Returns:
            A dictionary holding the JSON representation of the template.

        '''
        payload = {'template_type': 'button',
                   'text': self.text,
                   'buttons': [button.to_json() for button in self.buttons]}

        # Call the parent Template class with the payload
        return super().to_json(payload)


class ListTemplate(Template):
    '''A class representing a list template.

    Attributes:
        elements: A list of Elements to include in the list.
        button: A Button to include at the end of the list.
        compact: A boolean. If False, the first Element is expanded to fill
                 the top of the list. Otherwise, all items are rendered the
                 same way. Defaults to True.

    '''
    def __init__(self, elements, button=None, compact=True):

        # The Send API allows two to four elements only.
        if len(elements) in range(2, 5):
            self.elements = elements
        else:
            error = 'List templates require 2, 3, or 4 Elements'
            raise BoomerangException(error)

        self.button = button

        # Ensure the template is valid when in non-compact form.
        if not compact and elements[0].image_url is None:
            error = ('"image_url" must be present in the first element'
                     'of a non-compact list template')
            raise BoomerangException(error)

        self.compact = True

    def to_json(self):
        '''Converts the template to JSON.

        Returns:
            A dictionary holding the JSON representation of the template.

        '''
        payload = {'template_type': 'list',
                   'elements': [element.to_json() for element in
                                self.elements]}

        # While the Send API says that only one button may be used, it must
        # be within a list.
        if self.button is not None:
            payload['buttons'] = [self.button.to_json()]

        # Set the template style
        compact_styles = {True: 'compact', False: 'large'}
        payload['top_element_style'] = compact_styles[self.compact]

        # Call the parent Template class with the payload
        return super().to_json(payload)


class GenericTemplate(Template):
    '''A class representing a generic template.

    Attributes:
        elements: A list of Elements to include in the list.

    '''
    def __init__(self, elements):

        # The Send API allows up to 10 elements only.
        if len(elements) in range(1, 11):
            self.elements = elements
        else:
            error = 'Generic templates require between 1 and 10 Elements'
            raise BoomerangException(error)

    def to_json(self):
        '''Converts the template to JSON.

        Returns:
            A dictionary holding the JSON representation of the template.

        '''
        payload = {'template_type': 'generic',
                   'elements': [element.to_json() for element in
                                self.elements]}

        # Call the parent Template class with the payload
        return super().to_json(payload)


class Element:
    '''A class representing an element of the ListTemplate and GenericTemplate.

    Attributes:
        title: The name of the element.
        sub_title: A subtitle to display on the element.
        image_url: The URL of an image to display on the element.
        default_action: A DefaultAction to trigger when the element is pressed.
        buttons: A list of Buttons to add to the element.

    '''
    def __init__(self, title, sub_title=None, image_url=None,
                 default_action=None, buttons=None):
        self.title = title
        self.sub_title = sub_title
        self.image_url = image_url
        self.default_action = default_action
        self.buttons = buttons

    def to_json(self):
        '''Converts the element to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        json = {'title': self.title}

        if self.sub_title is not None:
            json['subtitle'] = self.sub_title

        if self.image_url is not None:
            json['image_url'] = self.image_url

        if self.default_action is not None:
            json['default_action'] = self.default_action.to_json()

        if self.buttons is not None:
            json['buttons'] = [button.to_json() for button in self.buttons]

        return json


class DefaultAction:
    '''A class representing an Element's default action, i.e. launching a
    URL.

    Attributes:
        url: The url to open when the element is pressed.

    '''
    def __init__(self, url):
        self.url = url

    def to_json(self):
        '''Converts the action to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': 'web_url',
                'url': self.url}
