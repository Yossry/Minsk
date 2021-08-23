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
import time

import requests


_logger = logging.getLogger(__name__)

# CHECK IF OPENZWAVE IS INSTALLED. ELSE THROW EXCEPTION
import sys, os
import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import six
if six.PY3:
    from pydispatch import dispatcher
else:
    from louie import dispatcher



class zwave_lock(models.Model):
    _inherit = 'zwave.node'


    lock_value = fields.Integer(string='The ZWaveValue ID', compute='_compute_doorlock_value')
    # time is an integer where 0 == no autolock and 1 - 2147483647
    lock_delay = fields.Integer(string='Delay before locking', compute='_compute_autolock')


    @api.depends('node_id')
    def _compute_doorlock_value(self):
        network = self.network_id.get_network()
        lock_values = network.nodes[self.node_id].get_doorlocks()
        for val, value_object in lock_values.items():
            # _logger.info("Returning value: %s"%val)
            self.lock_value = val

    @api.depends('node_id')
    def _compute_autolock(self):
        self.lock_delay = self.get_autolock().data

    @api.model
    def get_locked_status(self):
        network = self.network_id.get_network()
        locks = network.nodes[self.node_id].get_doorlocks()
        for val, value_object in locks.items():
            return value_object.data

    @api.multi
    def alert_autolock(self):
        lock = self.get_node()
        autolock_value = lock.get_values(label='Autolock')
        for val, value_object in autolock_value.items():
            raise Warning(value_object.data)

    @api.multi
    def get_autolock(self):
        lock = self.get_node()
        autolock_value = lock.get_values(label='Autolock')
        for val, value_object in autolock_value.items():
            return value_object

    @api.multi
    def set_autolock(self):
        # time is an integer where 0 == no autolock and 1 - 2147483647
        lock_delay = time or self.lock_delay
        autolock = self.get_autolock()
        autolock.data = self.lock_delay
        autolock.refresh()

    @api.multi
    def alert_state(self):
        network = self.network_id.get_network()
        locks = network.nodes[self.node_id].get_doorlocks()
        for val, value_object in locks.items():
            raise Warning(value_object.data)


    @api.multi
    def lock(self):

        lock = self.get_node()
        # Setting lock to True = locked
        lock.set_doorlock(self.lock_value, True)

    @api.multi
    def unlock(self):
        # value = self.get_doorlock_value()
        lock = self.get_node()
        # Setting lock to False = unlocked
        lock.set_doorlock(self.lock_value, False)