Webserver
=========

Installation
------------

#. Open Settings from the Now Playing icon
#. Select OBS WebSocket from the list of available input sources.
#. Check Enable
#. Change any settings as desired. See below.
#. Click Save

Settings
--------

.. image:: images/webserver.png
   :target: images/webserver.png
   :alt: Webserver settings screen

.. list-table::
   :header-rows: 1

   * - Setting
     - Description
   * - Port
     - The HTTP server's TCP port.  For security reasons, a firewall should protect this port to limit which hosts
       will be permitted to connect.
   * - HTML Template
     - The `Jinja2 template <https://jinja.palletsprojects.com/en/2.11.x/templates/>`_ file that will be used when the song
       updates when fetching index.html. See `Templates <../templatevariables.html>`_ for more information.
   * - Once
     - Only give index.html once per title, then giving a page that does nothing but refresh until the next song change.
       This setting is very useful to provide a simple way to do fade-in, fade-out using very simple HTML.


OBS Settings
------------

Once the webserver is enabled, hop into OBS and configure a Browser source.  Set the size to match
the HTML template you are using.  (Check the ``width`` and ``height`` values in the bundled templates).
Then place the OBS source wherever you would like.

.. image:: images/obs-browser-settings.png
   :target: images/obs-browser-settings.png
   :alt: OBS webserver settings screen



Supported URLs
--------------

.. list-table::
   :header-rows: 1

   * - URL
     - Description
   * - /index.html (or /index.htm or just /)
     - This URL generates either a title card based upon the preconfigured template or
       a refresh document.  The title card will be given exactly once upon connection with
       the refresh document being returned in subsequent connections until a new track has
       been detected.  This process allows for using fades and other HTML tricks.
   * - /index.txt
     - Same output as the text output in the General settings.
   * - /cover.png
     - This URL will return the cover image, if available.

REST API
--------

Currently, only a very rudimentary REST API is implememnted.  ``/v1/last`` will return
a JSON-formatted string of the currently playing track.


WebSockets
----------

New with version 3.0.0 is a continual feed via WebSockets. The feed is a JSON-formatted stream that
will get an update on every title change.  To connect, use the URL ``ws://hostname:port/wsstream``

Variables set should match what is on the `Templates <../templatevariables.html>`_ page. Be aware that
values may be null.
