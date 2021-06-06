#!/usr/bin/env python3
''' WebServer process '''

import asyncio
import base64
import logging
import logging.config
import os
import secrets
import signal
import string
import sys
import threading
import time
import weakref

import requests
import aiohttp
from aiohttp import web, WSCloseCode
import aiosqlite

from PySide2.QtCore import QStandardPaths  # pylint: disable=no-name-in-module

#
# quiet down our imports
#

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

# pylint: disable=wrong-import-position

import nowplaying.bootstrap
import nowplaying.config
import nowplaying.db
import nowplaying.utils

INDEXREFRESH = \
    '<!doctype html><html lang="en">' \
    '<head><meta http-equiv="refresh" content="5" ></head>' \
    '<body></body></html>\n'


TRANSPARENT_PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC'\
                                   '1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAA'\
                                   'ASUVORK5CYII=')


class WebHandler():
    ''' aiohttp built server that does both http and websocket '''
    def __init__(self, databasefile):
        threading.current_thread().name = 'WebServer'
        config = nowplaying.config.ConfigFile()
        self.port = config.cparser.value('weboutput/httpport', type=int)
        enabled = config.cparser.value('weboutput/httpenabled', type=bool)
        self.databasefile = databasefile

        while not enabled:
            try:
                time.sleep(5)
                config.get()
                enabled = config.cparser.value('weboutput/httpenabled',
                                               type=bool)
            except KeyboardInterrupt:
                sys.exit(0)

        self.magicstopurl = ''.join(
            secrets.choice(string.ascii_letters) for i in range(32))
        logging.info('Secret url to quit websever: %s', self.magicstopurl)

        signal.signal(signal.SIGINT, self.forced_stop)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(
            self.start_server(host='0.0.0.0', port=self.port))
        self.loop.run_forever()

    async def indexhtm_handler(self, request):  # pylint: disable=unused-argument
        ''' handle static index.html '''
        htmloutput = ""
        request.app['config'].get()
        metadata = request.app['metadb'].read_last_meta()
        lastid = await self.getlastid(request)
        template = request.app['config'].cparser.value(
            'weboutput/htmltemplate')
        once = request.app['config'].cparser.value('weboutput/once', type=bool)

        # | dbid  |  lastid | once |
        # |   x   |   NA    |      |  -> update lastid, send template
        # |   x   |  diff   |   NA |  -> update lastid, send template
        # |   x   |  same   |      |  -> send template
        # |   x   |  same   |   x  |  -> send refresh
        # |       |   NA    |      |  -> send refresh because not ready or something broke

        if not metadata or 'dbid' not in metadata or not template:
            return web.Response(status=202,
                                content_type='text/html',
                                text=INDEXREFRESH)

        if lastid == 0 or lastid != metadata['dbid'] or not once:
            await self.setlastid(request, metadata['dbid'])
            templatehandler = nowplaying.utils.TemplateHandler(
                filename=template)
            htmloutput = templatehandler.generate(metadata)
            return web.Response(content_type='text/html', text=htmloutput)

        return web.Response(content_type='text/html', text=INDEXREFRESH)

    async def setlastid(self, request, lastid):
        ''' get the lastid sent by http/html '''
        await request.app['statedb'].execute(
            'UPDATE lastprocessed SET lastid = ? WHERE id=1', [lastid])
        await request.app['statedb'].commit()

    async def getlastid(self, request):
        ''' get the lastid sent by http/html '''
        cursor = await request.app['statedb'].execute(
            'SELECT lastid FROM lastprocessed WHERE id=1')
        row = await cursor.fetchone()
        if not row:
            lastid = 0
        else:
            lastid = row[0]
        await cursor.close()
        return lastid

    async def indextxt_handler(self, request):
        ''' handle static index.txt '''
        metadata = request.app['metadb'].read_last_meta()
        txtoutput = ""
        if metadata:
            request.app['config'].get()
            templatehandler = nowplaying.utils.TemplateHandler(
                filename=request.app['config'].cparser.value(
                    'textoutput/txttemplate'))
            txtoutput = templatehandler.generate(metadata)
        return web.Response(text=txtoutput)

    async def favicon_handler(self, request):
        ''' handle favicon.ico '''
        return web.FileResponse(path=request.app['config'].iconfile)

    async def cover_handler(self, request):
        ''' handle cover image '''
        metadata = request.app['metadb'].read_last_meta()
        if 'coverimageraw' in metadata:
            return web.Response(content_type='image/png',
                                body=metadata['coverimageraw'])
        return web.Response(content_type='image/png', body=TRANSPARENT_PNG)

    async def api_v1_last_handler(self, request):
        ''' handle static index.txt '''
        metadata = request.app['metadb'].read_last_meta()
        return web.json_response(metadata)

    async def websocket_lastjson_handler(self, request, websocket):
        ''' handle singular websocket request '''
        metadata = request.app['metadb'].read_last_meta()
        if 'coverimageraw' in metadata:
            del metadata['coverimageraw']
        del metadata['dbid']
        await websocket.send_json(metadata)

    async def websocket_streamer(self, request):
        ''' handle continually streamed updates '''
        async def do_update(websocket, database):
            # early launch can be a bit weird so
            # pause a bit
            await asyncio.sleep(1)
            metadata = database.read_last_meta()
            if 'coverimageraw' in metadata:
                del metadata['coverimageraw']
            del metadata['dbid']
            await websocket.send_json(metadata)
            return time.time()

        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        request.app['websockets'].add(websocket)

        try:
            mytime = await do_update(websocket, request.app['metadb'])
            while True:
                while mytime > request.app['watcher'].updatetime:
                    await asyncio.sleep(1)

                mytime = await do_update(websocket, request.app['metadb'])
                await asyncio.sleep(1)
        except Exception as error:  #pylint: disable=broad-except
            logging.debug(error)
        finally:
            logging.debug('ended in finally')
            await websocket.close()
            request.app['websockets'].discard(websocket)
        return websocket

    async def websocket_handler(self, request):
        ''' handle inbound websockets '''
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        request.app['websockets'].add(websocket)
        try:
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        await websocket.close()
                    elif msg.data == 'last':
                        logging.debug('got last')
                        await self.websocket_lastjson_handler(
                            request, websocket)
                    else:
                        await websocket.send_str(
                            'some websocket message payload')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logging.error('ws connection closed with exception %s',
                                  websocket.exception())
        finally:
            request.app['websockets'].discard(websocket)

        return websocket

    def create_runner(self):
        ''' setup http routing '''
        threading.current_thread().name = 'WebServer-runner'
        app = web.Application()
        app['websockets'] = weakref.WeakSet()
        app.on_startup.append(self.on_startup)
        app.on_cleanup.append(self.on_cleanup)
        app.on_shutdown.append(self.on_shutdown)
        app.add_routes([
            web.get('/', self.indexhtm_handler),
            web.get('/v1/last', self.api_v1_last_handler),
            web.get('/cover.png', self.cover_handler),
            web.get('/favicon.ico', self.favicon_handler),
            web.get('/index.htm', self.indexhtm_handler),
            web.get('/index.html', self.indexhtm_handler),
            web.get('/index.txt', self.indextxt_handler),
            web.get('/ws', self.websocket_handler),
            web.get('/wsstream', self.websocket_streamer),
            web.get(f'/{self.magicstopurl}', self.stop_server)
        ])
        return web.AppRunner(app)

    async def start_server(self, host="127.0.0.1", port=8899):
        ''' start our server '''
        runner = self.create_runner()
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

    async def on_startup(self, app):
        ''' setup app connections '''
        app['config'] = nowplaying.config.ConfigFile()
        app['metadb'] = nowplaying.db.MetadataDB()
        app['watcher'] = app['metadb'].watcher()
        app['watcher'].start()
        app['statedb'] = await aiosqlite.connect(self.databasefile)
        app['statedb'].row_factory = aiosqlite.Row
        cursor = await app['statedb'].cursor()
        await cursor.execute('CREATE TABLE IF NOT EXISTS lastprocessed ('
                             'id INTEGER, '
                             'lastid INTEGER '
                             ')')
        await cursor.execute(
            'INSERT INTO lastprocessed (id, lastid) VALUES (1,0)')
        await app['statedb'].commit()

    async def on_shutdown(self, app):
        ''' handle shutdown '''
        for websocket in set(app['websockets']):
            await websocket.close(code=WSCloseCode.GOING_AWAY,
                                  message='Server shutdown')

    async def on_cleanup(self, app):
        ''' cleanup the app '''
        await app['statedb'].close()
        app['watcher'].stop()

    async def stop_server(self, request):  # pylint: disable=unused-argument
        ''' stop our server '''
        await request.app.shutdown()
        await request.app.cleanup()
        self.loop.stop()

    def forced_stop(self, signum, frame):  # pylint: disable=unused-argument
        ''' caught an int signal so tell the world to stop '''
        try:
            logging.debug('telling webserver to stop via http')
            requests.get(f'http://localhost:{self.port}/{self.magicstopurl}')
        except Exception as error:  # pylint: disable=broad-except
            logging.info(error)


def stop(pid):
    ''' stop the web server -- called from Tray '''
    logging.info('sending INT to %s', pid)
    try:
        os.kill(pid, signal.SIGINT)
    except ProcessLookupError:
        pass


def start(bundledir):
    ''' multiprocessing start hook '''
    threading.current_thread().name = 'WebServer'

    if not bundledir:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundledir = getattr(sys, '_MEIPASS',
                                os.path.abspath(os.path.dirname(__file__)))
        else:
            bundledir = os.path.abspath(os.path.dirname(__file__))

    nowplaying.bootstrap.set_qt_names()
    databasefile = os.path.join(
        QStandardPaths.standardLocations(QStandardPaths.CacheLocation)[0],
        'web.db')
    if os.path.exists(databasefile):
        try:
            os.unlink(databasefile)
        except PermissionError as error:
            logging.error('WebServer process already running?')
            logging.error(error)
            sys.exit(0)

    config = nowplaying.config.ConfigFile(bundledir=bundledir)  # pylint: disable=unused-variable
    logging.info('boot up')
    webserver = WebHandler(databasefile)  # pylint: disable=unused-variable


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start(None)
