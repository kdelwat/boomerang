from boomerang import Messenger, messages

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAAAT2Tz2ONZAqb2bbfbgiMKZASZBzoCZCmKuD5R4RUeJPbgsLkHSA5yd621CTWcRD0kwuAZCSKgjLtFJvPorpsct62oyFdjsUZBDm80aJcLMSNDtr3mqlH5SJeqPF8PyrL4UMtC0cZArQZAou1WwykkZCy8ABJlYRkAZDZD'


class EchoServer(Messenger):

    async def message_received(self, message):

        # Print the received message
        print('\nReceived message from {0}'.format(message.user_id))
        print('> {0}'.format(message.text))

        # Send the new Message object
        message_id = await self.send_action(message.user_id, 'typing_on')

        print('Reply sent with message id: {0}'.format(message_id))


app = EchoServer(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True)
