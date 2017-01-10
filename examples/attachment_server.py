from boomerang import Messenger, messages

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAAAT2Tz2ONZAqb2bbfbgiMKZASZBzoCZCmKuD5R4RUeJPbgsLkHSA5yd621CTWcRD0kwuAZCSKgjLtFJvPorpsct62oyFdjsUZBDm80aJcLMSNDtr3mqlH5SJeqPF8PyrL4UMtC0cZArQZAou1WwykkZCy8ABJlYRkAZDZD'


class EchoServer(Messenger):

    async def message_received(self, message):
        try:
            # Print the received message
            print('\nReceived message from {0}'.format(message.user_id))
            print('> {0}'.format(message.text))

            # Inform the sender that their message is being processed.
            # await self.acknowledge(message)

            # Create a Message object with the text received
            # reply = messages.Message(text=message.text)

            attachment = await self.host_attachment('image',
                                                    '/home/cadel/test.JPG')
            print(attachment.url)
            reply = messages.Message(attachment=attachment)
            message_id = await self.respond_to(message, reply)
            print('Reply sent with message id: {0}'.format(message_id))

        except Exception as e:
            print(e)


app = EchoServer(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True, base_url='https://47f86ce2.ngrok.io')
