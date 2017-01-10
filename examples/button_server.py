from boomerang import Messenger, messages, buttons

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAELVVEsfZAYBecAbs97NkJ7faaW3U5uZCMsoc1PdEZAku6ZBHYB7CKoEqqJb8egQc8FVZA2ZARF5UTysvCKEKokiukTFZAd5pSRYj7qTJilzz3jZCZAhZBMgIh9zjLfKZAYk8QcbMfUKoKVEbWKW8293QAj2ZCTzeIZC9AgZDZD'

class MyMessenger(Messenger):

    async def message_received(self, message):
        print('\nReceived message from {0}'.format(message.user_id))
        print('> {0}'.format(message.text))
        try:
            url_button = buttons.URLButton('Google', 'http://www.google.com')
            postback_button = buttons.PostbackButton('Postback', 'dummy_payload')
            call_button = buttons.CallButton('Call', '+15105551234')
            print('It is not the buttons')
            attachment = messages.ButtonTemplate('Select a URL', [url_button,
                                                                    postback_button,
                                                                    call_button])
            print('It is not the attachment')
            reply = messages.Message(attachment=attachment)
            print('It is not the reply')

            message_id = await self.send(message.user_id, reply)
            print('It is not the sending')
        except Exception as e:
            print('EXCEPTION: ' + str(e))
        print('MID: ' + str(message_id))

app = MyMessenger(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True)
