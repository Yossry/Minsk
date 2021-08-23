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
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import logging
import odoo
import erppeek

import traceback

import time

_logger = logging.getLogger(__name__)

class run(models.AbstractModel):
    _inherit = 'rfid.run'

    @api.model
    def run(self, barcode):
        """ The inherited instance of rfid_scanner.py  """
        server_url = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.server_url1')
        database = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.database_name1')
        username = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.username1')
        password = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.password1')
        match = None

        if barcode:
            # Checks with the cache first to speed up lock and unlock response
            match = self.env['hr.cache'].search([('barcode', '=', barcode)], limit=1)
            client = None
            # Talks with the server if the cache is not found
            if not match:
                if all([server_url, database, username, password]):
                    _logger.info("GOT HERE")
                    try:
                        client = erppeek.Client(server_url, database, username, password)
                        match = client.search('hr.employee', [('barcode', '=', barcode)], limit=1)
                        employee_id = client.model('hr.employee').browse(match)

                        if employee_id:
                            employee = employee_id.id[0]
                            cache = self.env['hr.cache'].search([('employee_id', '=', employee)], limit=1)
                            if not cache:
                                self.env['hr.cache'].create({
                                    'barcode':barcode,
                                    'employee_id':employee
                                    })
                                _logger.info("CREATED CACHE OBJECT")
                            
                    except:
                        _logger.warn("Something went wrong: \n %s"%traceback.format_exc())


                else:
                    _logger.warn("No config parameter found for either server_url or password.")

            # If the barcode check was successful we unlock the lock
            if match:
                network = ''
                if not self.env['zwave.network'].search([]):
                    network = self.env['zwave.network'].create({})
                else:
                    network = self.env['zwave.network'].search([], limit=1)

                if network.state() != 10:
                    network.start()

                if not self.env['zwave.node'].search([]):
                    _logger.info("Mapping nodes..")
                    network.map_nodes()
                lock = self.env['zwave.node'].search([('node_id', '=', 2)], limit=1)

                if lock:
                    state = lock.get_locked_status()
                    lock.unlock()
            else:
                _logger.info("BARCODE DOES NOT MATCH")

            
            #update cache If it has not been created.
            if not client:
                client = erppeek.Client(server_url, database, username, password)
                match = client.search('hr.employee', [('barcode', '=', barcode)], limit=1)
                try:
                    employee_id = client.model('hr.employee').browse(match)
                    employee = employee_id.id[0]

                    cache = self.env['hr.cache'].search([('employee_id', '=', employee)], limit=1)
                    _logger.info("Employee: %s"%employee)
                    if cache:
                        cache.employee_id = employee
                        cache.barcode = barcode
                    else:
                        _logger.warn("COULD NOT UPDATE CACHE")
                except:
                    _logger.warn("Something went wrong: \n %s"%traceback.format_exc())

