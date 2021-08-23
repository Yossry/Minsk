# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SetElement(models.Model):
    _description = 'Set Element'
    _name = 'clv.set.element'

    set_id = fields.Many2one(
        comodel_name='clv.set',
        string='Set',
        required=False
    )

    notes = fields.Text(string='Notes')


class Set(models.Model):
    _inherit = 'clv.set'

    set_element_ids = fields.One2many(
        comodel_name='clv.set.element',
        inverse_name='set_id',
        string='Elements',
        readonly=True
    )
    count_set_elements = fields.Integer(
        string='Number of Elements',
        compute='_compute_count_set_elements',
        store=False
    )

    @api.depends('set_element_ids')
    def _compute_count_set_elements(self):
        for r in self:
            r.count_set_elements = len(r.set_element_ids)
