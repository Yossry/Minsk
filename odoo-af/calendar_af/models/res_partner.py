# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    appointment_ids = fields.One2many(comodel_name='calendar.appointment', string='Booked meetings', inverse_name="partner_id")

    @api.one
    def _compute_appointment_count(self):
        for partner in self:
            partner.appointment_count = len(partner.appointment_ids)

    appointment_count = fields.Integer(compute='_compute_appointment_count')

    @api.multi
    def view_appointments(self):
        return{
            'name': _('Booked meetings'),
            'domain':[('partner_id', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'calendar.appointment',
            'view_id': self.env.ref('calendar_af.view_calendar_appointment_tree').id,
            'view_mode': 'tree', 
            'type': 'ir.actions.act_window',
        }