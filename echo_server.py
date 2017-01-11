from boomerang import Messenger, messages, events
import logging

VERIFY_TOKEN = 'secret_code'
PAGE_TOKEN = 'EAADJEe1tgFsBAAAT2Tz2ONZAqb2bbfbgiMKZASZBzoCZCmKuD5R4RUeJPbgsLkHSA5yd621CTWcRD0kwuAZCSKgjLtFJvPorpsct62oyFdjsUZBDm80aJcLMSNDtr3mqlH5SJeqPF8PyrL4UMtC0cZArQZAou1WwykkZCy8ABJlYRkAZDZD'

app = Messenger(VERIFY_TOKEN, PAGE_TOKEN)


@app.handle(events.MESSAGE_RECEIVED)
async def message_received(message):

    logging.info('Handler called')

    # Print the received message
    logging.info('\nReceived message from {0}'.format(message.user_id))
    logging.info('> {0}'.format(message.text))

    # Inform the sender that their message is being processed.
    await app.acknowledge(message)
    logging.info('Acknowledged message')

    # Create a Message object with the text received
    reply = messages.Message(text=message.text)

    # Send the new Message object
    message_id = await app.respond_to(message, reply)
    logging.info('Reply sent with message id: attribute{0}'.format(message_id))


if __name__ == '__main__':
    app.run(hostname='0.0.0.0', debug=True)
