Upgrading
=========

Be sure to check the
`changelog <https://github.com/whatsnowplaying/whats-now-playing/blob/main/CHANGELOG.md>`_ and the
`release notes <https://github.com/whatsnowplaying/whats-now-playing/releases>`_ for any
breaking changes and news.

From 2.x.x
----------

#. Install as normal. Upon launch, most settings will get copied over to their
   new homes in the new Settings screen.
#. Many templates have been added and updated. New templates will be copied into
   the templates directory. For updated templates, there are two outcomes:

   * If there have been no changes to the one in the template directory, the updated
     template file will overwrite the existing one.
   * If there have been changes to the one in the template directory, the updated one
     will be be put in as ``.new`` and will likely require you to take action. The existing
     one will be left there, however.  A pop-up on program launch will also inform you
     that the conflict has happened.

From 1.x.x
----------

Welcome aboard!

Unfortunately, 1.x.x wasn't built in a way to make it possible to upgrade from
one version to another.  So none of your settings are preserved.  You will need
to treat it as though it is a fresh install.
