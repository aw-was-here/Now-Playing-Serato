Serato
======

Serato is a commercial software package that runs on Mac OS X and Windows.  Now Playing
has two modes with which it may use Serato as an input: Local and Remote.

In Local mode, Now Playing will read the local session data on your computer directly.
This mode has much more data available to use but requires Now Playing to run on the
DJ computer.

In Remote mode, Now Playing will read
`Serato Live Playlists
<https://support.serato.com/hc/en-us/articles/228019568-Live-Playlists>`_
over the Internet.  This mode allows for Now Playing to run on a different computer
than the DJ computer, but does not have as much data available.

Instructions
------------

#. Open Settings from the Now Playing icon
#. Select Input Source from left-hand column

.. image:: images/serato-source-selection.png
   :target: images/serato-source-selection.png
   :alt: Serato Source Selection

#. Select the Serato from the list of available input sources.
#. Select Serato from the left-hand column.
#. Configure either Local or Remote mode as appropriate (see below)
#. Click Save

Local Mode
^^^^^^^^^^

.. image:: images/serato-local.png
   :target: images/serato-local.png
   :alt: Local Mode Settings


When Local Mode is active,  the **Now Playing** app runs on the same machine as Serato.  Configure the Serato Library Path to
Serato's directory, usually ``Music/_Serato_``.  This method is the recommended installation as much more information is available
and significantly improves **Now Playing**\ 's correctness.

Remote Mode
^^^^^^^^^^^


.. image:: images/serato-remote.png
   :target: images/serato-remote.png
   :alt: Remote Mode Settings


Remote mode is useful when the streaming computer is not the same as the Serato DJ computer but the HTTP Server
Mode cannot be used.


#.
   In Serato, make sure you enable Live Playlists and start a new session. From the `Serato website <https://support.serato.com/hc/en-us/articles/228019568-Live-Playlists>`_\ :

   ..

      "To enable the Live Playlists feature, go to the Expansion Pack tab on the Setup screen and check the Enable Live Playlists
      option. Once enabled, the Start Live Playlist button is now displayed in the History panel. Click this to start and stop your Live
      Playlist session."

#.
   Once a new playlist session is started, Serato will automatically open your web browser to your Live Playlist. **IMPORTANT:** You
   will need to select "Edit Details" on the Live Playlist webpage and change your playlist to "Public", or else the **Now Playing**
   app will not be able to retrieve any song data. The webpage does not need to remain open.  So you can close it once you ensure that
   the playlist has been made public.

#.
   Start the **Now Playing** app.  The app can be controlled and configured by accessing the menu from the icon in the Windows system tray or Mac menu bar.

Be aware that as of this writing (2021-03-05), the only information available via Live Playlists is the artist and the title
due to limitations on the Serato-side.
