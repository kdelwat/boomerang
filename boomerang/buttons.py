class URLButton:
    '''A class representing a URL button.

    Attributes:
        text: The text to display on the button.
        url: The url to open when the button is pressed.

    '''
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def to_json(self):
        '''Converts the button to JSON.

        Returns:
            A dictionary holding the JSON representation of the button.

        '''
        return {'type': 'web_url',
                'title': self.text,
                'url': self.url}
