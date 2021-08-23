# -*- coding: utf-8 -*-

import logging
import time

from pyusb_scale.scale import Scale
from threading import Thread, Lock

from odoo import http

import odoo.addons.hw_proxy.controllers.main as hw_proxy
import odoo.addons.hw_scale.controllers.main as hw_scale

_logger = logging.getLogger(__name__)

# Why not register as your own driver?
# POS looks at the status of the 'scale' driver
# instead of just trying to read from the scale
# if you have the scale enabled.
DRIVER_NAME = 'scale'


class ScaleThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.scalelock = Lock()
        self.status = {'status':'connecting', 'messages':[]}
        self.weight = 0
        self.weight_info = 'ok'
        self.device = None

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
                    _logger.error('Scale Error: '+ message)
                elif status == 'disconnected' and message:
                    _logger.warning('Disconnected Scale: '+ message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

            if status == 'error' and message:
                _logger.error('Scale Error: '+ message)
            elif status == 'disconnected' and message:
                _logger.info('Disconnected Scale: %s', message)

    def _parse_weight_answer(self, reading):
        """ Parse a scale's reading to a weighing request, returning
            a `(weight, weight_info, status)` pair.
        """
        weight, weight_info, status = None, None, None
        try:
            weight = reading.weight
            unit = reading.unit
            weight_info = reading.status

            if unit == 'kilogram':
                pass
            elif unit == 'pound':
                weight /= 2.20462
            elif unit == 'ounce':
                weight /= 35.274
            elif unit == 'gram':
                weight /= 1000.0
            else:
                raise Exception('Unsupported unit: %s' % (unit,))
        except Exception as e:
            _logger.exception("Cannot parse scale answer [%r] : %s", reading, e)
            status = ("Could not weigh on scale")
        return weight, weight_info, status

    def get_device(self):
        if self.device:
            return self.device

        return Scale()

    def get_weight(self):
        self.lockedstart()
        return self.weight

    def get_weight_info(self):
        self.lockedstart()
        return self.weight_info

    def get_status(self):
        self.lockedstart()
        return self.status

    def read_weight(self):
        with self.scalelock:
            try:
                reading = self.device.weigh()
                weight, weight_info, status = self._parse_weight_answer(reading)
                if status:
                    self.set_status('error', status)
                    self.device = None
                else:
                    if weight is not None:
                        self.weight = weight
                    if weight_info is not None:
                        self.weight_info = weight_info
            except Exception as e:
                self.set_status(
                    'error',
                    "Could not weigh on scale")
                self.device = None

    def set_zero(self):
        pass

    def set_tare(self):
        pass

    def clear_tare(self):
        pass

    def run(self):
        self.device = None

        while True:
            if self.device:
                old_weight = self.weight
                self.read_weight()
                if self.weight != old_weight:
                    _logger.info('New Weight: %s, sleeping %ss', self.weight, 0.2)
                    time.sleep(0.2)
                else:
                    _logger.info('Weight: %s, sleeping %ss', self.weight, 0.2)
                    time.sleep(0.2)
            else:
                with self.scalelock:
                    self.device = self.get_device()
                    if self.device:
                        self.set_status('connected')
                if not self.device:
                    # retry later to support "plug and play"
                    time.sleep(10)


scale_thread = ScaleThread()
hw_proxy.drivers[DRIVER_NAME] = scale_thread


class ScaleDriver(hw_scale.ScaleDriver):
    @http.route('/hw_proxy/scale_read/', type='json', auth='none', cors='*')
    def scale_read(self):
        if scale_thread.get_device():
            return {'weight': scale_thread.get_weight(),
                    'unit': 'kg',
                    'info': scale_thread.get_weight_info()}
        return super(ScaleDriver, self).scale_read()

    @http.route('/hw_proxy/scale_zero/', type='json', auth='none', cors='*')
    def scale_zero(self):
        if scale_thread.get_device():
            scale_thread.set_zero()
            return True
        return super(ScaleDriver, self).scale_read()

    @http.route('/hw_proxy/scale_tare/', type='json', auth='none', cors='*')
    def scale_tare(self):
        if scale_thread.get_device():
            scale_thread.set_tare()
            return True
        return super(ScaleDriver, self).scale_read()

    @http.route('/hw_proxy/scale_clear_tare/', type='json', auth='none', cors='*')
    def scale_clear_tare(self):
        if scale_thread.get_device():
            scale_thread.clear_tare()
            return True
        return super(ScaleDriver, self).scale_read()
