from boomerang import Messenger, messages, buttons

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAAAT2Tz2ONZAqb2bbfbgiMKZASZBzoCZCmKuD5R4RUeJPbgsLkHSA5yd621CTWcRD0kwuAZCSKgjLtFJvPorpsct62oyFdjsUZBDm80aJcLMSNDtr3mqlH5SJeqPF8PyrL4UMtC0cZArQZAou1WwykkZCy8ABJlYRkAZDZD'


class EchoServer(Messenger):

    async def message_received(self, message):
        try:
            # Print the received message
            print('\nReceived message from {0}'.format(message.user_id))
            print('> {0}'.format(message.text))

            button_list = [buttons.URLButton('Google', 'http://www.google.com'),
                           buttons.PostbackButton('Hit me', 'mmmmmm')]
            await self.set_thread_settings(menu_buttons=button_list,
                                           account_link_url='https://cadelwatson.com',
                                           whitelisted_domains=['https://google.com'],
                                           get_started_payload='payload',
                                           greeting_text='hi there')
            print('Reply sent')
        except Exception as e:
            print(e)


app = EchoServer(VERIFY_TOKEN, PAGE_TOKEN)
app.run(hostname='0.0.0.0', debug=True, base_url='https://47f86ce2.ngrok.io')
