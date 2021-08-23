# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Address(models.Model):
    _inherit = 'clv.address'

    family_history_ids = fields.One2many(
        comodel_name='clv.family.history',
        inverse_name='ref_address_id',
        string='Families (History)'
    )
    count_family_histories = fields.Integer(
        string='Families (History) (count)',
        compute='_compute_count_family_historiess',
    )

    @api.depends('family_history_ids')
    def _compute_count_family_historiess(self):
        for r in self:
            r.count_family_histories = len(r.family_history_ids)


class FamilyHistory(models.Model):
    _inherit = 'clv.family.history'

    ref_address_id = fields.Many2one(
        comodel_name='clv.address',
        string='Address',
        ondelete='restrict'
    )
