# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import
from logging import getLogger
from subprocess import call
from urllib2 import urlopen
from flexget import plugin
from flexget.event import event
from flexget.plugin import PluginError, RequestException
from flexget import validator
import time

log = getLogger('jdownloader')


class PluginJDownloader(object):
    """
    Add url from entry url to jDownloader

      jdownloader:
        api-mode: [flashgot|cnl|remotecontrol]
        api: http://127.0.0.1:9666/flashgot
        grabber: true
        start: false
        runcmd: /home/user/.jd/jd.sh

    Example::

      jdownloader:
        api-mode: cnl
        api: http://127.0.0.1:9666/flash
        runcmd: /home/user/.jd/jd.sh

    Example2::

      jdownloader:
        api-mode: remotecontrol
        api: http://127.0.0.1:10025
        grabber: true
        start: false
        runcmd: c:\Program Files (x86)\JDownloader\JDownloader.exe

    Example3::

      jdownloader:
        api-mode: flashgot
        api: http://127.0.0.1:9666/flashgot
        grabber: true
        start: false
        runcmd: c:\Program Files (x86)\JDownloader\JDownloader.exe

    Default values for the config elements::

      jdownloader:
        api-mode: flashgot
        api: http://127.0.0.1:9666/flashgot
        grabber: false
        start: false
    """

    __author__ = 'darodi http://jdownloader.org'
    __version__ = '0.7'

    DEFAULT_API_URL = 'http://127.0.0.1:9666/flashgot'
    DEFAULT_API_MODE = "flashgot"

    def validator(self):
        root = validator.factory()
        root.accept('boolean')
        config = root.accept('dict')
        config.accept('text', key='api-mode')
        config.accept('text', key='runcmd')
        config.accept('text', key='api')
        config.accept('boolean', key='grabber')
        config.accept('boolean', key='start')

        return root

    def prepare_config(self, config):
        if config is True:
            config = {'enabled': config}
            config.setdefault('api', self.DEFAULT_API_URL)
            config.setdefault('api-mode', self.DEFAULT_API_MODE)
        elif config is False:
            return

        return config

    def on_task_output(self, task, config):
        config = self.prepare_config(config)
        if not config.get('enabled', True):
            return
        if not task.accepted:
            return

        api_mode = config.get('api-mode', self.DEFAULT_API_MODE)
        url = config.get('api', self.DEFAULT_API_URL)
        runcmd = config.get('runcmd', '')

        if api_mode == 'remotecontrol':
            add_url = url.rstrip("/") + "/action/add/links/"
            if config.get('grabber', False):
                add_url += "grabber1/"
            else:
                add_url += "grabber0/"
            if config.get('start', False):
                add_url += "start1/"
            else:
                add_url += "start0/"

        elif api_mode == 'cnl' or api_mode == 'flashgot':
            add_url = url.rstrip("/") + "/add/"

        else:
            api_mode = 'flashgot'
            add_url = url.rstrip("/") + "/add/"

        try:
            response = task.requests.get(url)
        except RequestException:
            if runcmd == '':
                raise PluginError('jdownloader not reachable', log)
            else:
                call(runcmd)
                time.sleep(30)
                try:
                    response = task.requests.get(url)
                except RequestException:
                    raise PluginError('jdownloader not reachable', log)

        response.encoding = None
        if api_mode == 'cnl':
            if response.content != 'JDownloader\r\n':
                raise PluginError('jdownloader not reachable', log)
            for entry in task.accepted:
                try:
                    post_data = {'urls': str(entry['url']),
                                 'source': str(entry['url'])}
                    response = task.requests.post(add_url, data=post_data)
                    log.info('Package added: %s' % response.content)
                except Exception as e:
                    entry.fail(str(e))

        elif api_mode == 'remotecontrol':
            if response.content != 'JDRemoteControl - Malformed Request. use /help':
                raise PluginError('jdownloader not reachable', log)

            for entry in task.accepted:
                try:
                    download_url = str(add_url) + str(entry['url'])
                    reply = urlopen(download_url).read()
                    log.info('Package added: %s' % reply)
                except Exception as e:
                    entry.fail(str(e))

        elif api_mode == 'flashgot':

            autostart = '0'
            if config.get('start', False):
                autostart = '1'

            for entry in task.accepted:
                try:
                    post_data = {'urls': str(entry['url']), 'description': str(entry['title']),
                                 'autostart': autostart, 'package': str(entry['title']), 'referer': str(entry['original_url'])}
                    response = task.requests.post(add_url, data=post_data)
                    log.info('Package added: %s' % str(entry['url']))
                except Exception as e:
                    entry.fail(str(e))


@event('plugin.register')
def register_plugin():
    plugin.register(PluginJDownloader, 'jdownloader', api_ver=2)
