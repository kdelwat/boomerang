===============
Creating an App
===============

This guide will walk you through the steps of creating an app on the Messenger
Platform, and is largely based on Facebook's `quickstart guide`_. When you have
completed it, you will have a Facebook app set up for local hosting, ready to
develop.

First-time setup
----------------

1. Ensure you are logged into your Facebook account, which will be used for
   development. The category should be 'Apps for Messenger'.
2. Go to the Facebook `Apps`_ page and select 'Add a New App' to create your new
   development app.
3. Create a page for your app at `Create a Page`_.
4. Navigate to your App Dashboard. In the sidebar, select 'Messenger' and
   scroll down to 'Token Generation'. Select your page to generate a *page
   access token*, which will allow access to the Send API. Make a note of this
   token.
5. Think of a *verify token* for the Messenger Platform. This can be any string,
   and is used by Facebook to authenticate with your server.
6. Install `ngrok`_. You will use this to create an internet-accessible tunnel
   to the local server.
7. Install Boomerang, following :ref:`installation`.
8. Create a file called ``main.py`` and insert the following code to create an
   example echo server::

    from boomerang import Messenger, messages

    # Set the app's API access tokens, provided by Facebook
    VERIFY_TOKEN = 'your_webhook_token_here'
    PAGE_TOKEN = 'your_page_access_token_here'


    class EchoServer(Messenger):

        # Override the message_received method to handle received messages
        async def message_received(self, message):

            # Print the received message
            print('Received message from {0}'.format(message.user_id))
            print('> {0}'.format(message.text))

            # Inform the sender that their message is being processed
            await self.acknowledge(message)

            # Create a Message object with the text received
            reply = messages.Message(text=message.text)

            # Send the new Message object
            message_id = await self.respond_to(message, reply)

            print('Reply sent with message id: {0}'.format(message_id))


    app = EchoServer(VERIFY_TOKEN, PAGE_TOKEN)
    app.run(hostname='0.0.0.0', debug=True)

   Your *verify token* and *page access token* should replace those in the code
   above.

Starting a development session
------------------------------

The following steps must be taken before each local development session. It may
look like a lot, but one you follow the process once it only takes 2-3 minutes.

1. Run ngrok. On a Unix system, the following command is used:

   .. code-block:: console

      $ ./ngrok http 0.0.0.0:8000

2. Make a note of your *secure forwarding URL*, which ngrok will display. It
   should start with ``https://`` and look something like
   ``https://47f86ce2.ngrok.io``.
3. Go to your App Dashboard. If this is your first time setting up a webhook
   for the app, select 'Messenger' in the sidebar, then 'Setup Webhooks'.
   Otherwise, select 'Webhooks' in the sidebar and 'Edit' to edit the existing
   subscription.
4. The *Callback URL* is simply your *secure forwarding URL* combined with
   ``/webhook``, like ``https://47f86ce2.ngrok.io/webhook``.
5. The *Verify Token* is your *verify token* that you thought up during initial
   set-up.
6. The necessary subscription field for the echo server is 'messages', but it
   doesn't hurt to select all the options beginning with 'message' and
   'messaging'.
7. Select 'Messenger' in the sidebar, scroll to the 'Webhooks' section and
   select your page to subscribe to the webhook.
8. Run the script:

   .. code-block:: console

      $ python main.py

   This will run the server locally on the default port. Ngrok will connect the
   *secure forwarding url* to this local server.

You're all set! The server can be stopped and restarted at will during
development. If ngrok is stopped, however, re-running it will change your
*secure forwarding url* and you will need to change the *Callback URL* in the
App Dashboard.

.. _quickstart guide:
   https://developers.facebook.com/docs/messenger-platform/guides/quick-start
.. _Apps: https://developers.facebook.com/apps
.. _Create a Page: https://www.facebook.com/pages/create
.. _ngrok: https://ngrok.com/
