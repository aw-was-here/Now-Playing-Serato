MPRIS2
======

`MPRIS2 <https://mpris2.readthedocs.io/en/latest/>`_ is a specification for Linux DBus
compatible music software to communicate with each other.  Now Playing supports reading
track data from MPRIS2 sources, including VLC.  `Mixxx <https://mixxx.org>`_ is supported
with the appropriate PR added. See below.

In order to use MPRIS2 support, the dbus-python Python module must be installed in
the virtual environment.

Instructions
------------

#. Open Settings from the Now Playing icon
#. Select Input Source from left-hand column

.. image:: images/mpris2-input-source.png
   :target: images/mpris2-input-source.png
   :alt: mpris2-input-source

#. Select the MPRIS2 from the list of available input sources.
#. Select MPRIS2 from the left-hand column.
#. Select from the detected MPRIS2 sources.  Note that this list is not updated in
   real-time. Closing and re-opening the Settings UI will update the list.

.. image:: images/mpris2-source-selection.png
   :target: images/mpris2-source-selection.png
   :alt: mpris2-input-source

#. Click Save

Mixxx
~~~~~

Currently, Mixxx does not have out-of-the-box support for MPRIS2.  However,
`PR 3483 <https://github.com/mixxxdj/mixxx/pull/3483>`_ adds support. As of this writing,
that PR does not contain support for the `xesam:url` field, which limits its usabilty
with Now Playing.  `This fork <https://github.com/aw-was-here/mixxx/tree/mpris2>`_ is
usually up-to-date with main+PR 3483+xesam url support.