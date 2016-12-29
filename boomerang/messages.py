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
