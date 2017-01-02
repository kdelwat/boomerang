import abc

from .exceptions import BoomerangException

class Button(metaclass=abc.ABCMeta):
    '''The abstract base class for all button types.

    Attributes:
        button_type: The type of the button.
        text: The text to display on the button. Due to the Send API's
              limitation, it cannot be more than 20 characters long.

    '''
    def __init__(self, button_type, text):
        self.button_type = button_type

        if len(text) > 20:
            error = 'Text on buttons may not be more than 20 characters long'
            raise BoomerangException(error)
        else:
            self.text = text


class URLButton(Button):
    '''A class representing a URL button.

    Attributes:
        text: The text to display on the button.
        url: The url to open when the button is pressed.

    '''
    def __init__(self, text, url):
        super().__init__('web_url', text)

        self.url = url

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': self.button_type,
                'title': self.text,
                'url': self.url}


class PostbackButton(Button):
    '''A class representing a postback button.

    Attributes:
        text: The text to display on the button.
        payload: The string to send to the webhook as a postback, when the
                 button is clicked.

    '''
    def __init__(self, text, payload):
        super().__init__('postback', text)

        self.payload = payload

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': self.button_type,
                'title': self.text,
                'payload': self.payload}


class ShareButton(Button):
    '''A class representing a share button, which can only be present inside
    a generic template.

    '''
    def __init__(self):
        self.button_type = 'element_share'

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': self.button_type}


class CallButton(Button):
    '''A class representing a call button, which triggers a phone call.

    Attributes:
        text: The text to display on the button.
        phone_number: A string representing a phone number
                      (including area code).

    '''
    def __init__(self, text, phone_number):
        super().__init__('phone_number', text)

        self.phone_number = phone_number

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': self.button_type,
                'title': self.text,
                'payload': self.phone_number}


class QuickReply:
    '''A class representing quick-reply buttons.

    Attributes:
        button_type: The type of the button, either 'text' or 'location'.
        text: The text to display on the button. Due to the Send API's
              limitation, it cannot be more than 20 characters long. Only
              available when button_type is 'text'.
        payload: The payload string that will be returned to the webhook when
                 the button is pressed. Only available when button_type is
                 'text'.
        image_url: The URL of an image to use on the button. Only available
                   when button_type is 'text'.

    '''
    def __init__(self, button_type, text=None, payload=None, image_url=None):

        # Ensure that only a valid button type is chosen.
        if button_type not in ['text', 'location']:
            error = "QuickReply button_type must be 'text' or 'location'"
            raise BoomerangException(error)

        self.button_type = button_type

        # Initialise a text button.
        if button_type == 'text':
            if text is None or payload is None:
                error = "QuickReply text button must contain text and payload"
                raise BoomerangException(error)

            self.text = text
            self.payload = payload
            self.image_url = image_url

        # Initialise a location button, which can't take other parameters.
        else:
            if any(attr is not None for attr in [text, payload, image_url]):
                error = ('QuickReply location button cannot contain other'
                         'attributes')
                raise BoomerangException(error)

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        json = {'content_type': self.button_type}

        if self.button_type == 'text':
            json['title'] = self.text
            json['payload'] = self.payload

            if self.image_url is not None:
                json['image_url'] = self.image_url

        return json
