# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.config import config
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import logging
import odoo
import erppeek

import traceback

import requests

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
import time
from select import select
from threading import Thread, Lock

from odoo.addons.hw_proxy.controllers import main as hw_proxy
from odoo.modules.registry import Registry

from os import listdir
from os.path import join, isdir

import evdev


_logger = logging.getLogger(__name__)

scanner_thread = None


# This module does not work if hw_scanner module is running.

# IN PROGRESS
class RFID_Devices(models.Model):
    _name = "rfid.devices"
    
    # ~ listDevices = fields.Char(string="Available devices")
    device_path = fields.Char(string="Path to device")
    device_name = fields.Char(string="Device name")
    thread_state = fields.Boolean(string="State")



class run_method(models.AbstractModel):
    _name = "rfid.run"
    """ The syntax to run within the loop when a code got scanned successfully. """
    @api.model
    def run(self, barcode):
        """ Should be inherited """
        pass
        

class RFID_ScannerDevice():
    def __init__(self, path):
        self.evdev = evdev.InputDevice(path)
        self.evdev.grab()

        self.barcode = []
        self.shift = False

class RFID_Scanner(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.status = {'status':'connecting', 'messages':[]}
        self.input_dir = '/dev/input/by-id/'
        self.open_devices = []
        self.barcodes = Queue()
        self.env = None
        self.keymap = {
            2: ("1","!"),
            3: ("2","@"),
            4: ("3","#"),
            5: ("4","$"),
            6: ("5","%"),
            7: ("6","^"),
            8: ("7","&"),
            9: ("8","*"),
            10:("9","("),
            11:("0",")"),
            12:("-","_"),
            13:("=","+"),
            # 14 BACKSPACE
            # 15 TAB
            16:("q","Q"),
            17:("w","W"),
            18:("e","E"),
            19:("r","R"),
            20:("t","T"),
            21:("y","Y"),
            22:("u","U"),
            23:("i","I"),
            24:("o","O"),
            25:("p","P"),
            26:("[","{"),
            27:("]","}"),
            # 28 ENTER
            # 29 LEFT_CTRL
            30:("a","A"),
            31:("s","S"),
            32:("d","D"),
            33:("f","F"),
            34:("g","G"),
            35:("h","H"),
            36:("j","J"),
            37:("k","K"),
            38:("l","L"),
            39:(";",":"),
            40:("'","\""),
            41:("`","~"),
            # 42 LEFT SHIFT
            43:("\\","|"),
            44:("z","Z"),
            45:("x","X"),
            46:("c","C"),
            47:("v","V"),
            48:("b","B"),
            49:("n","N"),
            50:("m","M"),
            51:(",","<"),
            52:(".",">"),
            53:("/","?"),
            # 54 RIGHT SHIFT
            57:(" "," "),
        }

    def get_env(self):
        db = config.get('rfid_database')
        if not db:
            db = odoo.service.db.list_dbs()
            db = db and db[0] or ''

        cursor = Registry(db).cursor()

        cursor.autocommit(True)
        context = {}
        return api.Environment(cursor, SUPERUSER_ID, context)


    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def set_status(self, status, message = None):
        if status == self.status['status']:
            if message != None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            _logger.error('Barcode Scanner Error: '+message)
        elif status == 'disconnected' and message:
            _logger.info('Disconnected Barcode Scanner: %s', message)

    def get_devices(self):
        try:
            if not evdev:
                return []

            if not isdir(self.input_dir):
                return []

            new_devices = [device for device in listdir(self.input_dir)
                           if join(self.input_dir, device) not in [dev.evdev.fn for dev in self.open_devices]]
            scanners = [device for device in new_devices
                        if (('kbd' in device) and ('keyboard' not in device.lower()))
                        or ('barcode' in device.lower()) or ('scanner' in device.lower())]

            for device in scanners:

                # does not pick upp the named device
                
                with api.Environment.manage():
                    try:
                        env = self.get_env()
                        banned_devices = env['ir.config_parameter'].get_param('rfid_scanner.banned_devices')
                        if device not in banned_devices:
                            _logger.debug('opening device %s', join(self.input_dir,device))
                            self.open_devices.append(RFID_ScannerDevice(join(self.input_dir,device)))

                    except Exception as e:
                        _logger.warn(traceback.format_exc())
                        self.set_status('Enviroment error',str(e))
                    finally:
                        env.cr.close()


            if self.open_devices:
                self.set_status('connected','Connected to '+ str([dev.evdev.name for dev in self.open_devices]))
            else:
                self.set_status('disconnected','Barcode Scanner Not Found')

            return self.open_devices
        except Exception as e:
            self.set_status('error',str(e))
            return []

    def release_device(self, dev):
        self.open_devices.remove(dev)
        self.lockedstart()

        while True:
            try:
                timestamp, barcode = self.barcodes.get(True, 5)
                if timestamp > time.time() - 5:
                    return barcode
            except Empty:
                return ''

    def get_status(self):
        self.lockedstart()
        return self.status

    def _get_open_device_by_fd(self, fd):
        for dev in self.open_devices:
            if dev.evdev.fd == fd:
                return dev

    def run(self):
        """ This will start a loop that catches all keyboard events, parse barcode
            sequences and put them on a timestamped queue that can be consumed by
            the point of sale's requests for barcode events
        """
        self.barcodes = Queue()

        barcode  = []
        shift    = False
        devices  = None

        while True: # barcodes loop
            devices = self.get_devices()

            try:
                while True: # keycode loop
                    r,w,x = select({dev.fd: dev for dev in [d.evdev for d in devices]},[],[],5)
                    if len(r) == 0: # timeout
                        break

                    for fd in r:
                        device = self._get_open_device_by_fd(fd)

                        if not evdev.util.is_device(device.evdev.fn):
                            _logger.info('%s disconnected', str(device.evdev))
                            self.release_device(device)
                            break

                        events = device.evdev.read()

                        for event in events:
                            if event.type == evdev.ecodes.EV_KEY:
                                # _logger.debug('Evdev Keyboard event %s',evdev.categorize(event))
                                if event.value == 1: # keydown events
                                    if event.code in self.keymap:
                                        if device.shift:
                                            device.barcode.append(self.keymap[event.code][1])
                                        else:
                                            device.barcode.append(self.keymap[event.code][0])
                                    elif event.code == 42 or event.code == 54: # SHIFT
                                        device.shift = True
                                    elif event.code == 28: # ENTER, end of barcode
                                        _logger.debug('pushing barcode %s from %s', ''.join(device.barcode), str(device.evdev))
                                        self.barcodes.put( (time.time(),''.join(device.barcode)) )
                                        timestump, input_barcode = self.barcodes.get(True)


                                        with api.Environment.manage():
                                            try:
                                                env = self.get_env()

                                                hexadecimal_devices = env['ir.config_parameter'].get_param('rfid_scanner.hexadecimal_devices')
                                                # Converts input to decimal from hexadecimal for readers added.
                                                if device.evdev.name in hexadecimal_devices:
                                                    hexa_string = input_barcode
                                                    result = int(hexa_string, 16)
                                                    input_barcode = result
                                                env['rfid.run'].run(input_barcode)
                                                
                                            except Exception as e:
                                                _logger.warn(traceback.format_exc())
                                                self.set_status('Enviroment error',str(e))
                                            finally:
                                                env.cr.close()



                                        device.barcode = []
                                elif event.value == 0: #keyup events
                                    if event.code == 42 or event.code == 54: # LEFT SHIFT
                                        device.shift = False


            except Exception as e:
                _logger.warn(traceback.format_exc())
                self.set_status('error',str(e))


# Starts the threaded loop. lockedstart() starts it.
if evdev:
    scanner_thread = RFID_Scanner()
    hw_proxy.drivers['rfid'] = scanner_thread
    scanner_thread.lockedstart()