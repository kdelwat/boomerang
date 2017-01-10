from boomerang import Messenger, messages, buttons

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAELVVEsfZAYBecAbs97NkJ7faaW3U5uZCMsoc1PdEZAku6ZBHYB7CKoEqqJb8egQc8FVZA2ZARF5UTysvCKEKokiukTFZAd5pSRYj7qTJilzz3jZCZAhZBMgIh9zjLfKZAYk8QcbMfUKoKVEbWKW8293QAj2ZCTzeIZC9AgZDZD'


class MyMessenger(Messenger):

    async def message_received(self, message):
        print('\nReceived message from {0}'.format(message.user_id))
        print('> {0}'.format(message.text))
        text_button = buttons.QuickReply('text', text='Button',
                                            payload='button_pressed',
                                            image_url='http://www.google.com')
        location_button = buttons.QuickReply('location')
        reply = messages.Message(text='Choose a button',
                                    quick_replies=[text_button,
                                                location_button])

        message_id = await self.send(message.user_id, reply)

        print('MID: ' + str(message_id))


app = MyMessenger(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True)
