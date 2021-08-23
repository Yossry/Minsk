# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Insured(models.Model):
    _inherit = 'clv.insured'

    set_element_ids = fields.One2many(
        string='Set Elements',
        comodel_name='clv.set.element',
        compute='_compute_set_element_ids_and_count',
    )
    count_sets = fields.Integer(
        string='Sets',
        compute='_compute_set_element_ids_and_count',
    )

    @api.multi
    def _compute_set_element_ids_and_count(self):
        for record in self:
            set_elements = self.env['clv.set.element'].search([
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ])
            record.count_sets = len(set_elements)
            record.set_element_ids = [(6, 0, set_elements.ids)]
