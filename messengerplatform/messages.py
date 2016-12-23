import abc


class BaseMessage(metaclass=abc.ABCMeta):
    '''The BaseMessage class is the base class for all messages sent to the bot.
    It handles the User ID and timestamp of the message. BaseMessage is
    subclassed by all other types of message, which must implement both the
    from_json() factory method and the to_json() method.

    .. py:class:: BaseMessage(user_id, timestamp)

        :param int user_id:   The Messenger ID of the user who triggered the
                              message.
        :param int timestamp: The timestamp (in milliseconds since epoch) of
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
    '''The Message class holds Message Received events.

    .. py:class:: Message(user_id, timestamp, text='', attachments=[],
                          quick_reply=None, message_id=None,
                          sequence_position=None)

        :param int user_id:   The Messenger ID of the user who triggered the
                              message.
        :param int timestamp: The timestamp (in milliseconds since epoch) of
                              the message.
        :param str text: The text of the message.
        :param list attachments: A list of Attachment objects.
        :param QuickReply quick_reply: A QuickReply holding a payload set by
                                       the bot for quick replies.
        :param str message_id: The Messenger ID of the message.
        :param int sequence_position: The position of the message in the
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
        '''Factory that builds a Message object from JSON provided by the
        API.

        :param int user_id: The Messenger ID of the user who triggered the
                            message.
        :param int timestamp: The timestamp (in milliseconds since epoch) of
                              the message.
        :param dict json: A JSON representation that is converted into the
                          Message object.

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
    '''The MediaAttachment class holds media attachments.

    .. py:class:: MediaAttachment(media_type, url)

        :param str media_type: The type of the attachment. Can be one of
                               'image', 'audio', 'video', or 'file'.
        :param str url: The url of the media.

    '''

    def __init__(self, media_type, url):
        self.media_type = media_type
        self.url = url

    @classmethod
    def from_json(cls, json):
        '''Factory that builds a MediaAttachment object from JSON provided by the
        API.

        :param dict json: A JSON representation that is converted into the
                          MediaAttachment object.

        '''
        return cls(json['type'], json['payload']['url'])

    def to_json(self):
        return


class LocationAttachment(BaseMessage):
    '''The LocationAttachment class holds location attachments.

    .. py:class:: LocationAttachment(latitude, longitude)

        :param float latitude: The latitude of the location.
        :param float longitude: The longitude of the location.

    '''

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_json(cls, json):
        '''Factory that builds a LocationAttachment object from JSON provided
        by the API.

        :param dict json: A JSON representation that is converted into the
                          LocationAttachment object.

        '''
        return cls(json['payload']['coordinates']['lat'],
                   json['payload']['coordinates']['long'])

    def to_json(self):
        return


class QuickReply:
    '''The QuickReply class holds a developer-specified payload.

    .. py:class:: QuickReply(payload)

        :param str payload: The payload of the quick reply returned by the API.

    '''

    def __init__(self, payload):
        self.payload = payload

    @classmethod
    def from_json(cls, json):
        '''Factory that builds a QuickReply object from JSON provided
        by the API.

        :param dict json: A JSON representation that is converted into the
                          QuickAttachment object.

        '''
        return cls(json['payload'])
