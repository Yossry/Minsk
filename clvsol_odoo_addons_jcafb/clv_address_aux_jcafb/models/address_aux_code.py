# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AddressAux(models.Model):
    _name = "clv.address_aux"
    _inherit = 'clv.address_aux', 'clv.abstract.code'

    code = fields.Char(string='Address Code', required=False, default=False)
    code_sequence = fields.Char(default='clv.address.code')

    @api.multi
    def _address_aux_set_code(self):

        for address_aux in self:

            if address_aux.code is False:

                vals = {}

                if address_aux.related_address_id.id is not False:
                    vals['code'] = address_aux.related_address_id.code

                else:
                    vals['code'] = '/'

                address_aux.write(vals)
