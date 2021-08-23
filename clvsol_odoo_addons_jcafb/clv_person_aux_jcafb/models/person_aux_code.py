# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PersonAux(models.Model):
    _name = "clv.person_aux"
    _inherit = 'clv.person_aux', 'clv.abstract.code'

    code = fields.Char(string='Person Code', required=False, default=False)
    code_sequence = fields.Char(default='clv.person.code')

    @api.multi
    def _person_aux_set_code(self):

        for person_aux in self:

            if person_aux.code is False:

                vals = {}

                if person_aux.related_person_id.id is not False:
                    if person_aux.related_person_id.code is not False:
                        vals['code'] = person_aux.related_person_id.code
                    else:
                        vals['code'] = '/'

                else:
                    vals['code'] = '/'

                person_aux.write(vals)
