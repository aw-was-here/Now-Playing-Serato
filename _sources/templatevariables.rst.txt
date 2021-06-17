Templates
=========

Now Playing handles almost all output via the
`Jinja2 templating system <https://jinja2docs.readthedocs.io/>`_ which
includes an extremely `powerful language <https://jinja2docs.readthedocs.io/en/stable/templates.html>`_
that enables you a full range of customizing the output.

In general, Now Playing provides a generic set of variables that can be used in any template. These
values are filled in dependent on a few factors:

* the input source providing its own data
* whether the media has been appropriately tagged
* Now Playing's ability to read those tags

Some examples:

* An MP3 file missing ID3 tags may only have `title` available.
* Serato in Remote mode, title and optionally artist are available.
* MP4 files have very limited support currently in Now Playing so will not have the label

Additionally, some outputs (e.g., TwitchBot) may provide additional variables that provide
additional, context-sensitive features. See their individual pages for more information.

Support Variables
-----------------

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
   * - album
     - Album track comes from
   * - albumartist
     - Artist listed on the album
   * - artist
     - Artist for the song
   * - bitrate
     - Bitrate the file was encoded at
   * - bpm
     - Beats per minute of the song
   * - composer
     - Composer of the song
   * - coverurl
     - Relative location to fetch the cover. Note that this will only work when the webserver is active.
   * - date
     - Date of the media
   * - deck
     - deck # this track is playing on
   * - disc
     - Disc number
   * - disc_total
     - Total number of discs in album
   * - filename
     - Local filename of the media
   * - genre
     - Genre of the song
   * - key
     - Key of the song
   * - label
     - Label of the media
   * - lang
     - Language used by the media
   * - title
     - Title of the media
   * - track
     - Track number on the disc
   * - track_total
     - Total tracks on the disc


Implementation Notes
--------------------

Arrays
^^^^^^

Fields that are may be multi-valued (e.g., genre) will be merged into one.

Undefined
^^^^^^^^^

When rendering templates, Now Playing will set any undefined variables to the empty string.
Instead of having to render a template as:

.. code-block:: jinja2

  {% if variable is defined and variable is not none and variable|length %}

This can be short-cut to:

.. code-block:: jinja2

  {% if variable %}

Since variable will always be defined. This fact also means that templates that mistakenly use the
wrong variable name will render, just with an empty string in place of the expected text.
