#!/usr/bin/env python3

import logging
import os
import threading
import time

import obswebsocket
import obswebsocket.requests

import nowplaying.config
import nowplaying.db

from PySide2.QtCore import Signal, QThread  # pylint: disable=no-name-in-module


class OBSWebSocketHandler(QThread):
    ''' Talk to OBS Directly '''

    obswsenable = Signal(bool)

    def __init__(self, parent=None):
        self.config = nowplaying.config.ConfigFile()
        QThread.__init__(self, parent)
        self.client = None
        self.endthread = False
        self.metadb = nowplaying.db.MetadataDB()
        self.text = None
        self.obswsport = None
        self.obswssecret = None
        self.obswshost = None

    def run(self):
        ''' run our thread '''
        threading.current_thread().name = 'OBSWebSocket'

        while not self.endthread:
            logging.debug('Starting main loop')
            self.config.get()

            while self.config.getpause() or not self.config.cparser.value(
                    'obsws/enabled', type=bool):
                time.sleep(5)
                self.config.get()
                if self.endthread:
                    break

            if self.endthread:
                break

            source = self.config.cparser.value('obsws/source')
            if not source:
                continue

            time.sleep(
                self.config.cparser.value('settings/interval', type=float))

            self.check_reconnect()
            self.text = self.generate_text()
            if self.text:
                try:
                    if self.config.cparser.value('obsws/freetype2'):
                        self.client.call(
                            obswebsocket.requests.SetTextFreetype2Properties(
                                source=source, text=self.text))
                    else:
                        self.client.call(
                            obswebsocket.requests.SetTextGDIPlusProperties(
                                source=source, text=self.text))
                except:  # pylint: disable=bare-except
                    # there are a lot of uncaught, internal exceptions from
                    # upstream :(

                    pass

    def generate_text(self, clear=False):
        ''' convert template '''
        metadata = self.metadb.read_last_meta()
        if not metadata:
            return None

        template = self.config.cparser.value('obsws/template')
        templatehandler = nowplaying.utils.TemplateHandler(filename=template)
        if templatehandler:
            txttemplate = templatehandler.generate(metadatadict=metadata)
        elif clear:
            txttemplate = ''
        else:
            txttemplate = '{{ artist }} - {{ title }}'

        return txttemplate

    def check_reconnect(self):
        ''' check if our params have changed and if so reconnect '''
        obswshost = self.config.cparser.value('obsws/host')
        try:
            obswsport = self.config.cparser.value('obsws/port', type=int)
        except TypeError:
            self.obswsenable.emit(False)

        obswssecret = self.config.cparser.value('obsws/secret')

        reconnect = False
        if not self.obswshost or self.obswshost != obswshost:
            reconnect = True

        if not self.obswsport or self.obswsport != obswsport:
            reconnect = True

        if not self.obswssecret or self.obswssecret != obswssecret:
            reconnect = True

        if reconnect:
            self.obswssecret = obswssecret
            self.obswsport = obswsport
            self.obswshost = obswshost
            try:
                self.client = obswebsocket.obsws(obswshost, obswsport,
                                                 obswssecret)
                self.client.connect()
            except:  # pylint: disable=bare-except

                # there are a lot of uncaught, internal exceptions from
                # upstream :(

                self.obswsenable.emit(False)

    def exit(self):
        ''' exit the thread '''
        logging.debug('OBS WebSocket asked to stop')
        self.endthread = True
        if self.client:
            self.client.disconnect()
            self.client = None

    def __del__(self):
        logging.debug('OBS WebSocket thread is being killed!')
        self.exit()
