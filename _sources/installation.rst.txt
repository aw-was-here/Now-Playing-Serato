Installation
============

Linux
-----

Binaries are not provided because of dbus-python, so please follow the developer guide
to install in a Python virtual environment.  Note that currently, this software does
not run headless.

*Important note for Linux users*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to use MPRIS2, you *must* have dbus-python installed in your Python virtual
environment.

Mac
---

* Download the latest macOS release zip package
  `here <https://github.com/whatsnowplaying/whats-now-playing/releases/latest>`_.
* Unzip the archive and place the unzipped ``NowPlaying.app`` file in your ``Applications``
  folder or any other location that you desire.

*Important note for macOS users*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Due to security measures in macOS Sierra and later, unsigned apps may have limitations
placed on them.  These limitations will prevent them from operating correctly or even
opening at all. Opening the app on High Sierra and newer versions of macOS by following
the steps below. Versions before High Sierra have not been verified and are not currently
supported.

* Do not unzip the downloaded zip package directly to the folder from where you will be
  running it. Instead, unzip it in a location such as the ``Downloads`` folder
  and then move the ``NowPlaying.app`` to your destination folder (e.g.,
  "Applications"). Then run the app from the destination folder.
* If the app fails to open, try holding down the Control key and then double-clicking open.
* If after following the step above the app does not open, open Terminal and type:
  ``sudo xattr -r -d com.apple.quarantine /path/to/NowPlaying.app`` (replace with the
  correct path to the app).

Windows
-------

* Download the latest Windows release zip package
  `here <https://github.com/whatsnowplaying/whats-now-playing/releases/latest>`_.
* Unzip the package and copy the entire unzipped folder containing the
  ``NowPlaying.exe`` file and supporting files to the directory you'd like the app to
  run from (i.e., ``C:\Program Files``).

*Important note for Windows users*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Microsoft has beefed up Windows security and you may now get prompted about an unsigned
binary.  Click on 'More Info' and then 'Run Anyway' to launch Now Playing.
