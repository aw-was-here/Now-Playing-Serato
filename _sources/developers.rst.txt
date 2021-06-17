
Developers
==========

.. code-block:: text

       NOTE: For people familiar with Python, it is HIGHLY RECOMMENDED that you use and
       build with venv due to the restrictive requirements of the tested packages listing.
       While newer versions MAY work, there is no guarantee that PyInstaller and other
       utilities will build a proper executable.

Development Requirements
------------------------

To locally build and install **Now Playing**\ , you will need the following:

#. Python for your operating system (3.8 or higher is recommended)
#. Access to a development shell (e.g., /Applications/Utility/Terminal on OS X)
#. ``git`` installed and working

Linux Pre-work
^^^^^^^^^^^^^^

If you are on Linux, it is recommended that you install dbus-python at
the system level first in order to get the basic OS requirements put in
place first.  For example, for Debian-style systems:

.. code-block:: bash

   sudo apt-get install python-dbus

Commands
--------

.. code-block:: bash

   python -m venv (virtualenv directory)
   source (virtualenv directory)/bin/activate
   git clone https://github.com/whastnowplaying/whats-now-playing.git
   cd whats-now-playing
   pip install .

On Linux, install dbus-python in your virtual env:

.. code-block:: bash

   pip install dbus-python

At this point, you should be able to run the software from the shell:

.. code-block:: bash

   NowPlaying

Build Executable
----------------

To build a stand-alone executable, you will need to run PyInstaller:

.. code-block:: bash

   pyinstaller NowPlaying.spec

There should now be a ``dist`` directory and inside that directory will be
either a ``NowPlaying.app`` on OS X or just a ``NowPlaying`` single file.
