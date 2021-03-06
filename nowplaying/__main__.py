#!/usr/bin/env python3
''' NowPlaying as run via python -m '''
#import faulthandler
import logging
import multiprocessing
import os
import pathlib
import sys

from PySide2.QtCore import QCoreApplication, QStandardPaths, Qt  # pylint: disable=no-name-in-module
from PySide2.QtWidgets import QApplication  # pylint: disable=no-name-in-module

import nowplaying
import nowplaying.bootstrap
import nowplaying.config
import nowplaying.db
import nowplaying.systemtray


def run_bootstrap(bundledir=None):
    ''' bootstrap the app '''

    logpath = os.path.join(
        QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0],
        QCoreApplication.applicationName(), 'logs')
    pathlib.Path(logpath).mkdir(parents=True, exist_ok=True)
    logpath = os.path.join(logpath, "debug.log")

    nowplaying.bootstrap.setuplogging(logpath=logpath)

    nowplaying.bootstrap.upgrade(bundledir=bundledir)

    # fail early if metadatadb can't be configured
    metadb = nowplaying.db.MetadataDB()
    metadb.setupsql()


def main():
    ''' main entrypoint '''

    multiprocessing.freeze_support()
    #faulthandler.enable()

    # set paths for bundled files
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundledir = getattr(sys, '_MEIPASS',
                            os.path.abspath(os.path.dirname(__file__)))
    else:
        bundledir = os.path.abspath(os.path.dirname(__file__))

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    nowplaying.bootstrap.set_qt_names()
    run_bootstrap(bundledir=bundledir)

    config = nowplaying.config.ConfigFile(bundledir=bundledir)
    logging.getLogger().setLevel(config.loglevel)
    logging.captureWarnings(True)
    tray = nowplaying.systemtray.Tray()  # pylint: disable=unused-variable
    exitval = qapp.exec_()
    logging.info('shutting down v%s',
                 nowplaying.version.get_versions()['version'])
    sys.exit(exitval)


if __name__ == '__main__':
    main()
