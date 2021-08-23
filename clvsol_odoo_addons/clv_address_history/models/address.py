# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AddressHistory(models.Model):
    _inherit = 'clv.address.history'

    address_id = fields.Many2one(
        comodel_name='clv.address',
        string='Address',
        ondelete='restrict'
    )


class Address(models.Model):
    _inherit = 'clv.address'

    address_history_ids = fields.One2many(
        comodel_name='clv.address.history',
        inverse_name='address_id',
        string='Addresses (History)'
    )
    count_address_histories = fields.Integer(
        string='Addresses (History) (count)',
        compute='_compute_count_address_histories',
    )

    @api.depends('address_history_ids')
    def _compute_count_address_histories(self):
        for r in self:
            r.count_address_histories = len(r.address_history_ids)
