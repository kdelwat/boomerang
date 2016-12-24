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


class MessageDelivered(BaseMessage):
    '''A class holding Message Delivered events.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message event.
        watermark: An integer timestamp. All messages with a timestamp before
                   this message are guaranteed to have been delivered.
        message_ids: A list of string Messenger IDs of the delivered
                     messages.
        sequence_position: An integer position of the message in the
                           conversation sequence.

    '''

    def __init__(self, user_id, timestamp, watermark, message_ids,
                 sequence_position):
        self.user_id = user_id
        self.timestamp = timestamp
        self.watermark = watermark
        self.message_ids = message_ids
        self.sequence_position = sequence_position

    @classmethod
    def from_json(cls, user_id, timestamp, json):
        '''Builds a MessageDelivered object from JSON provided by the API.

        Args:
            user_id: An integer Messenger ID of the user who triggered the
                    message.
            timestamp: An integer timestamp (in milliseconds since epoch) of
                    the message.
            json: A dict containing the JSON representation that is converted
                  into the MessageDelivered object.

        Returns:
            A MessageDelivered object.

        '''

        # If message IDs aren't present, store an empty list.
        message_ids = json.get('mids', [])

        return cls(user_id, timestamp, json['watermark'], message_ids,
                   json['seq'])


class MessageRead(BaseMessage):
    '''A class holding Message Delivered events.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message event.
        watermark: An integer timestamp. All messages with a timestamp before
                   this message are guaranteed to have been read.
        sequence_position: An integer position of the event in the
                           conversation sequence.

    '''

    def __init__(self, user_id, timestamp, watermark, sequence_position):
        self.user_id = user_id
        self.timestamp = timestamp
        self.watermark = watermark
        self.sequence_position = sequence_position

    @classmethod
    def from_json(cls, user_id, timestamp, json):
        '''Builds a MessageRead object from JSON provided by the API.

        Args:
            user_id: An integer Messenger ID of the user who triggered the
                    message.
            timestamp: An integer timestamp (in milliseconds since epoch) of
                    the message.
            json: A dict containing the JSON representation that is converted
                  into the MessageRead object.

        Returns:
            A MessageRead object.

        '''

        return cls(user_id, timestamp, json['watermark'], json['seq'])


class Postback(BaseMessage):
    '''A class holding Postback events.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message event.
        payload: A string defined by the bot when creating the postback button.
        referral: An optional Referral object.

    '''

    def __init__(self, user_id, timestamp, payload, referral=None):
        self.user_id = user_id
        self.timestamp = timestamp
        self.payload = payload
        self.referral = referral

    @classmethod
    def from_json(cls, user_id, timestamp, json):
        '''Builds a Postback object from JSON provided by the API.

        Args:
            user_id: An integer Messenger ID of the user who triggered the
                    message.
            timestamp: An integer timestamp (in milliseconds since epoch) of
                    the message.
            json: A dict containing the JSON representation that is converted
                  into the MessageRead object.

        Returns:
            A Postback object.

        '''

        # Convert a referral to a Referral object if present
        if 'referral' in json:
            referral = Referral.from_json(user_id, timestamp, json['referral'])
        else:
            referral = None

        return cls(user_id, timestamp, json['payload'], referral)


class Referral(BaseMessage):
    '''A class holding Referral events.

    Attributes:
        user_id: An integer Messenger ID of the user who triggered the
                 message.
        timestamp: An integer timestamp (in milliseconds since epoch) of
                   the message event.
        data: A string passed by the referral link.

    '''

    def __init__(self, user_id, timestamp, data):
        self.user_id = user_id
        self.timestamp = timestamp
        self.data = data

    @classmethod
    def from_json(cls, user_id, timestamp, json):
        '''Builds a Referral object from JSON provided by the API.

        Args:
            user_id: An integer Messenger ID of the user who triggered the
                    message.
            timestamp: An integer timestamp (in milliseconds since epoch) of
                    the message.
            json: A dict containing the JSON representation that is converted
                  into the Referral object.

        Returns:
            A Referral object.

        '''

        return cls(user_id, timestamp, json['ref'])
