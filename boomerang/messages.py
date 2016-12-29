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

        return json
