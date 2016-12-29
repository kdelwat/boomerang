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
