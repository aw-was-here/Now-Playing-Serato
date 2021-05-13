#!/usr/bin/env python3
'''

This code originally:

Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not
use this file except in compliance with the License. A copy of the License
is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing permissions and
limitations under the License.
'''

import logging
import logging.handlers
import os
import sys
import threading
import time

import irc.bot
import jinja2
import requests
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from PySide2.QtCore import QCoreApplication, QStandardPaths, Qt  # pylint: disable=no-name-in-module

import nowplaying.config
import nowplaying.db


class TwitchBot(irc.bot.SingleServerIRCBot):  # pylint: disable=too-many-instance-attributes
    ''' twitch bot '''
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token.removeprefix("oauth:")
        self.channel = '#' + channel.lower()
        self.event_handler = None
        self.observer = None
        self.templatedir = os.path.join(
            QStandardPaths.standardLocations(
                QStandardPaths.DocumentsLocation)[0],
            QCoreApplication.applicationName(), 'templates')
        self.metadb = nowplaying.db.MetadataDB()
        self.config = nowplaying.config.ConfigFile()

        threading.current_thread().name = 'TwitchBot'

        self.jinja2 = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templatedir),
            autoescape=jinja2.select_autoescape(['htm', 'html', 'xml']))

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {
            'Client-ID': client_id,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        req = requests.get(url, headers=headers).json()
        if 'error' in req:
            logging.error('%s %s: %s', req['status'], req['error'],
                          req['message'])
            sys.exit(0)
        self.channel_id = req['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        logging.info('Connecting to %s on port %d', server, port)
        irc.bot.SingleServerIRCBot.__init__(self,
                                            [(server, port, 'oauth:' + token)],
                                            username, username)
        self._setup_timer()

    def _setup_timer(self):

        template = self.config.cparser.value('twitchbot/announce')
        if not template:
            return

        watchfile = self.config.cparser.value('textoutput/file')
        self.event_handler = PatternMatchingEventHandler(
            patterns=[os.path.basename(watchfile)],
            ignore_patterns=None,
            ignore_directories=True,
            case_sensitive=False)
        self.event_handler.on_closed = self._announce_track
        self.observer = Observer()
        self.observer.schedule(self.event_handler,
                               os.path.dirname(watchfile),
                               recursive=False)
        self.observer.start()

    def _announce_track(self, filename):  # pylint: disable=unused-argument
        self._post_template(
            os.path.basename(self.config.cparser.value('twitchbot/announce')))

    def on_welcome(self, connection, event):  # pylint: disable=unused-argument
        ''' join the IRC channel and set up our stuff '''
        logging.info('Joining %s', self.channel)

        # You must request specific capabilities before you can use them
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel)
        connection.privmsg(self.channel, '/me bot connected')

    def on_pubmsg(self, connection, event):  # pylint: disable=unused-argument
        ''' find commands '''
        commandchar = self.config.cparser.value('twitchbot/commandchar')
        if not commandchar:
            commandchar = '!'
            self.config.cparser.setValue('twitchbot/commandchar', '!')
        if event.arguments[0][:1] == commandchar:
            cmd = event.arguments[0].split(' ')[0][1:]
            logging.info('Received command: %s', cmd)
            self.do_command(event, cmd)

    def _build_user_profile(self, event):  #pylint: disable=no-self-use
        # Get the channel id, we will need this for v5 API calls
        tags = event.tags
        result = {}
        for entry in tags:
            result.update({entry['key']: entry['value']})
        return result

    def _post_template(self, template, moremetadata=None):
        metadata = self.metadb.read_last_meta()
        if 'coverimageraw' in metadata:
            del metadata['coverimageraw']

        if moremetadata:
            metadata.update(moremetadata)

        if os.path.isfile(os.path.join(self.templatedir, template)):
            template = self.jinja2.get_template(template)
            message = template.render(metadata)
            message = message.replace('\n', '')
            message = message.replace('\r', '')
            self.connection.privmsg(self.channel, str(message).strip())

    def do_command(self, event, command):  # pylint: disable=unused-argument
        ''' process a command '''
        metadata = {}
        fullstring = event.arguments[0]
        self._build_user_profile(event)
        commands = fullstring.split()
        commands[0] = commands[0][1:]
        if len(commands) > 1:
            counter = 0
            for target in commands[1:]:
                counter = counter + 1
                metadata[f'cmdtarget{counter}'] = target

        cmdfile = f'twitchbot_{commands[0]}.txt'

        if commands[0] == 'quit':
            self.shutdown()

        self._post_template(cmdfile, moremetadata=metadata)

    def shutdown(self):  # pylint: disable=no-self-use
        '''
        logging.info('Would shutdown but not sure how')'''
        self.observer.stop()
        self.observer.join()
        self.connection.privmsg(self.channel, '/me bye!')
        sys.exit(0)


class TwitchBotHandler():
    ''' Now Playing built-in web server using custom handler '''
    def __init__(self, config=None):
        self.config = config
        self.server = None
        self.endthread = False

    def run(self):  # pylint: disable=too-many-branches, too-many-statements
        '''
            run & configure a twitch bot

            The sleeps are here to make sure we don't
            tie up a CPU constantly checking on
            status.  If we cannot open the port or
            some other situation, we bring everything
            to a halt by triggering pause.

            But in general:

                - web server thread starts
                - check if web serving is running
                - if so, open ANOTHER thread (MixIn) that will
                  serve connections concurrently
                - if the settings change, then another thread
                  will call into this one via stop() to
                  shutdown the (blocking) serve_forever()
                - after serve_forever, effectively restart
                  the loop, checking what values changed, and
                  doing whatever is necessary
                - land back into serve_forever
                - rinse/repeat

        '''
        threading.current_thread().name = 'TwitchBotControl'

        while not self.endthread:
            logging.debug('Starting main loop')

            while not self.isconfigured():
                time.sleep(5)
                if self.endthread:
                    break

            if self.endthread:
                self.stop()
                break
            try:
                self.server = TwitchBot(
                    self.config.cparser.value('twitchbot/username'),
                    self.config.cparser.value('twitchbot/clientid'),
                    self.config.cparser.value('twitchbot/token'),
                    self.config.cparser.value('twitchbot/channel'))
            except Exception as error:  # pylint: disable=broad-except
                logging.error('TwitchBot threw exception on create: %s', error)

            try:
                self.server.start()
            except KeyboardInterrupt:
                pass
            except Exception as error:  # pylint: disable=broad-except
                logging.error('Web server threw exception after forever: %s',
                              error)
            finally:
                if self.server:
                    self.server.shutdown()

    def isconfigured(self):
        ''' need everything configured! '''
        if (not self.config.cparser.value('twitchbot/enabled', type=bool)
                or not self.config.cparser.value('twitchbot/username')
                or not self.config.cparser.value('twitchbot/clientid')
                or not self.config.cparser.value('twitchbot/token')
                or not self.config.cparser.value('twitchbot/channel')):
            return False
        return True

    def stop(self):
        ''' method to stop the thread '''
        logging.debug('asked to stop or reconfigure')
        if self.server:
            self.server.shutdown()

    def __del__(self):
        logging.debug('thread is being killed!')
        self.endthread = True
        self.stop()


def stop():
    ''' stop the web server -- called from Tray '''


def start(orgname, appname, bundledir):
    ''' multiprocessing start hook '''
    threading.current_thread().name = 'TwitchBot'

    if not orgname:
        orgname = 'com.github.em1ran'

    if not appname:
        appname = 'NowPlaying'

    if not bundledir:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundledir = getattr(sys, '_MEIPASS',
                                os.path.abspath(os.path.dirname(__file__)))
        else:
            bundledir = os.path.abspath(os.path.dirname(__file__))

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setOrganizationName(orgname)
    QCoreApplication.setApplicationName(appname)
    config = nowplaying.config.ConfigFile(bundledir=bundledir)
    logging.info('boot up')
    twitchbot = TwitchBotHandler(config)  # pylint: disable=unused-variable
    twitchbot.run()


def main():
    ''' integration test '''
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username = sys.argv[1]
    client_id = sys.argv[2]
    token = sys.argv[3]
    channel = sys.argv[4]

    orgname = 'com.github.em1ran'

    appname = 'NowPlaying'

    bundledir = os.path.abspath(os.path.dirname(__file__))

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setOrganizationName(orgname)
    QCoreApplication.setApplicationName(appname)
    # need to make sure config is initialized with something
    nowplaying.config.ConfigFile(bundledir=bundledir)
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == "__main__":
    main()
