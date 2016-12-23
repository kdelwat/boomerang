import abc


class BaseMessage(metaclass=abc.ABCMeta):
    '''The base class for all messages sent to the bot.

    This class handles the User ID and timestamp of all message. BaseMessage is
    subclassed by all other types of message, which must implement both the
    from_json() factory method and the to_json() method.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message.

    '''
    def __init__(self, user_id, timestamp):
        self.user_id = user_id
        self.timestamp = timestamp

    @abc.abstractclassmethod
    def from_json(cls, json):
        return

    @abc.abstractmethod
    def to_json(self):
        return


class Message(BaseMessage):
    '''A class holding Message Received events.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message.
        text: A string representing the text of the message.
        attachments: A list of Attachment objects.
        quick_reply: A QuickReply holding a payload set by
                     the bot for quick replies.
        message_id: An integer Messenger ID of the message.
        sequence_position: An integer position of the message in the
                           conversation sequence.

    '''

    def __init__(self, user_id, timestamp, text='', attachments=[],
                 quick_reply=None, message_id=None, sequence_position=None):
        self.user_id = user_id
        self.timestamp = timestamp
        self.text = text
        self.attachments = attachments
        self.quick_reply = quick_reply
        self.message_id = message_id
        self.sequence_position = sequence_position

    @classmethod
    def from_json(cls, user_id, timestamp, json):
        '''Builds a Message object from JSON provided by the API.

        Args:
            user_id: An integer Messenger ID of the user who triggered the
                    message.
            timestamp: An integer timestamp (in milliseconds since epoch) of
                    the message.
            json: A dict containing the JSON representation that is converted
                  into the Message object.

        Returns:
            A Message object.

        '''
        # Convert any quick reply to a Quick Reply object
        if 'quick_reply' in json:
            quick_reply = QuickReply.from_json(json['quick_reply'])
        else:
            quick_reply = None

        # Convert all attachments to Attachment objects
        attachments = []
        for attachment in json.get('attachments', []):
            if attachment['type'] == 'location':
                attachments.append(LocationAttachment.from_json(attachment))
            else:
                attachments.append(MediaAttachment.from_json(attachment))

        # Get text of message if available
        text = json.get('text', '')

        return cls(user_id, timestamp, text=text,
                   attachments=attachments, quick_reply=quick_reply,
                   message_id=json['mid'], sequence_position=json['seq'])

    def to_json(self):
        return


class MediaAttachment(BaseMessage):
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
        return


class LocationAttachment(BaseMessage):
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

    def to_json(self):
        return


class QuickReply:
    '''A class holding a developer-specified quick reply payload.

    Attributes:
        payload: The string payload of the quick reply returned by the API.

    '''

    def __init__(self, payload):
        self.payload = payload

    @classmethod
    def from_json(cls, json):
        '''Builds a QuickReply object from JSON provided by the API.

        Args:
            json: A dict containing the JSON representation that is converted
                  into the QuickAttachment object.

        Returns:
            A QuickReply object.

        '''
        return cls(json['payload'])
