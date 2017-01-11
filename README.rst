===============================
Boomerang
===============================


.. image:: https://img.shields.io/pypi/v/boomerang.svg
        :target: https://pypi.python.org/pypi/boomerang

.. image:: https://img.shields.io/travis/kdelwat/boomerang.svg
        :target: https://travis-ci.org/kdelwat/boomerang

.. image:: https://readthedocs.org/projects/boomerang/badge/?version=latest
        :target: https://boomerang.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/kdelwat/boomerang/shield.svg
     :target: https://pyup.io/repos/github/kdelwat/boomerang/
     :alt: Updates


Boomerang is an asynchronous Python library for building services on the
Facebook Messenger Platform. See the documentation at `ReadTheDocs`_!

Why should I use Boomerang?
---------------------------
* Requests are handled *asynchronously*, allowing for rapid handling of
  callbacks and messages. Boomerang is built on the incredibly fast `Sanic`_
  webserver, `uvloop`_ replacement for ``asyncio``'s event loop, and `aiohttp`_
  for asynchronous HTTP requests.
* Boomerang has *100% test coverage* and extensive documentation for learners.
* There are two options for interfacing with the Messenger Platform: use the
  high-level API which introduces abstractions like ``acknowledge``, which
  marks a received message as *seen* and displays a 'typing' icon while
  preparing the actual response; or use the low-level API for more flexibility
  and send actions individually.
* The library is open-source under the MIT License, and can be used for
  commercial purposes.

Why shouldn't I use Boomerang?
------------------------------
* The library uses Python 3.5's ``async`` and ``await`` syntax, as does the
  underlying Sanic server. If support for older versions is required, Boomerang
  isn't a great fit.
* Boomerang hosts its own server (Sanic), which allows for tightly-integrated
  and rapid handling. However, if you want to use a different server (like
  Flask), Boomerang isn't suitable.

Example
-------

The following example is a simple echo server. When a user sends a message to
the bot, the bot echoes the message back::

  from boomerang import Messenger, messages, events

  # Set the app's API access tokens, provided by Facebook
  VERIFY_TOKEN = 'your_webhook_token_here'
  PAGE_TOKEN = 'your_page_access_token_here'

  # Initialise the server
  app = Messenger(VERIFY_TOKEN, PAGE_TOKEN)

  @app.handle(events.MESSAGE_RECEIVED)
  async def message_received(self, message):

      # Print the received message
      print('Received message from {0}'.format(message.user_id))
      print('> {0}'.format(message.text))

      # Inform the sender that their message is being processed
      await self.acknowledge(message)

      # Return the message's text to respond
      return message.text

  app.run(hostname='0.0.0.0', debug=True)

Features
--------

* Support for the Webhook, Send, Thread Settings, and User Profile APIs.
* Full support for message templates.
* High- or low-level interface for sending messages.
* Automatic attachment hosting: the library can send a local file by serving
  it statically with a unique URL, which is passed to Messenger. This is
  cached meaning files are only served once, helping performance.

Credits
---------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template. Cookiecutter is really cool
and you should check it out!

.. _Sanic: https://github.com/channelcat/sanic
.. _uvloop: https://github.com/MagicStack/uvloop
.. _aiohttp: https://github.com/KeepSafe/aiohttp
.. _ReadTheDocs: https://boomerang.readthedocs.io.
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
