# -*- coding: utf-8 -*-

import logging
import time
import subprocess

from tempfile import NamedTemporaryFile
from threading import Thread, Lock
from base64 import b64decode

from odoo import http

import odoo.addons.hw_proxy.controllers.main as hw_proxy

_logger = logging.getLogger(__name__)

DRIVER_NAME = 'print_queue'


class PrintQueueThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.bashlock = Lock()
        self.status = {'status': 'connecting', 'messages': []}
        self.device = None
        self.device_command = 'lpstat -p default'

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def set_status(self, status, message=None):
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)

                if status == 'error' and message:
                    _logger.error('Print Error: ' + message)
                elif status == 'disconnected' and message:
                    _logger.warning('Printer Disconnected: ' + message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

            if status == 'error' and message:
                _logger.error('Print Error: ' + message)
            elif status == 'disconnected' and message:
                _logger.info('Disconnected Printer: %s', message)

    def get_device(self):
        if self.device:
            return self.device

        process = subprocess.Popen(self.device_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            _logger.warn('cannot get printer named \'default\'')
            return None
        else:
            return 'default'

    def print_attachment(self, attachment):
        printer = attachment.get('printer')
        if not printer:
            printer = 'default'
        if attachment['filename'].lower().find('.zpl') >= 0:
            raw = True
        else:
            raw = False
        with self.bashlock:
            with NamedTemporaryFile(delete=False) as f:
                f.write(b64decode(attachment['data']))
            cmd = 'lp -d ' + printer
            if raw:
                cmd += ' -o raw'
            cmd += ' ' + str(f.name)
            _logger.info('printing with full command: ' + cmd)
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                _logger.warn('print_attachment error: ' + str(error))
        return True

    def get_status(self):
        self.lockedstart()
        return self.status

    def run(self):
        self.device = None

        while True:
            if self.device:
                time.sleep(10)
            else:
                with self.bashlock:
                    self.device = self.get_device()
                    if self.device:
                        self.set_status('connected')
                if not self.device:
                    # retry later to support "plug and play"
                    time.sleep(10)


printer_thread = PrintQueueThread()
hw_proxy.drivers[DRIVER_NAME] = printer_thread


class PrintQueueDriver(hw_proxy.Proxy):
    @http.route('/hw_proxy/print_queue', type='json', auth='none', cors='*')
    def print_queue(self, attachment):
        # {
        #     mimetype: "application/octet-stream",
        #     id: 5344,
        #     name: "LabelFedex-787623177789.ZPLII",
        #     filename: "LabelFedex-787623177789.ZPLII",
        #     url: "/web/content/5344?download=true",
        #     data: base64blob
        # }
        printer_thread.print_attachment(attachment)

