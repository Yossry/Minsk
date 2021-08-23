# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import http
from odoo.http import request
from werkzeug import exceptions

import datetime
import json

import logging
_logger = logging.getLogger(__name__)

# exception.BadRequest() 400

class AfAppointments(http.Controller):

    @http.route('/appointments/appointments/', auth='user', website=False)
    def appointments(self):
        # TODO: GET + POST
        #self.env['calendar.occasion'].get_bookable_occasions()
        json = ''
        return json

    @http.route('/appointments/competences/', auth='user', website=False, type='http')
    def competences(self):
        """ Get a complete list of all meeting types in the system.
        !!! Odoo is not master for this data. This method should not be relied 
        upon !!!"""
        # NOTE: GET
        res_dict = []
        type_ids = request.env['calendar.appointment.type'].search([])
        for type_id in type_ids:
            res_dict.append({
                'id': type_id.ipf_id,
                'name': type_id.name
            })
        return json.dumps(res_dict, ensure_ascii=False)

    @http.route('/appointments/bookable-occasions/', auth='user', website=False)
    def bookable_occasions(self, appointment_type, appointment_length, 
    from_date, from_time, to_date, to_time, location_code, profession_id, 
    employee_user_id, max_depth):
        """Get bookable occasions"""
        # TODO: GET
        start = datetime.datetime.strptime("%sT%s" % (from_date, from_time), "%Y-%m-%dT%H:%M:%S")
        stop = datetime.datetime.strptime("%sT%s" % (to_date, to_time), "%Y-%m-%dT%H:%M:%S")
        type_id = request.env['calendar.appointment.type'].search([('ipf_id', '')])
        # TODO: ....
        request.env['calendar.occasion'].get_bookable_occasions(start, stop, type_id, channel, max_depth = 1)
        json = ''
        return json

    @http.route('/appointments/bookable-occasions/reservation', auth='user', website=False)
    def bookable_occasions_reservation(self, ocassion, **post):
        # TODO: POST + DELETE
        if post:
            if ocassions:
                ocassion_ids = self.env['calendar.occasion'].browse(ocassions)
                appointment_id = self.env[calendar.occasion].reserve_occasion(ocassion_ids)
                if appointment_id:
                    return 201
                else:
                    return '???'
            else:
                return 201
        else:
            return exception.BadRequest()
