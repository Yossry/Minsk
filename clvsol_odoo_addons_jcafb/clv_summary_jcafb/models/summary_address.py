# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryAddress(models.Model):
    _description = 'Summary Address'
    _name = 'clv.summary.address'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    address_id = fields.Many2one(
        comodel_name='clv.address',
        string='Address',
        ondelete='cascade'
    )
    address_global_tag_ids = fields.Many2many(
        string='Address Global Tags',
        related='address_id.global_tag_ids',
        store=False
    )
    address_category_ids = fields.Many2many(
        string='Address Categories',
        related='address_id.category_ids',
        store=False
    )
    address_state = fields.Selection(
        string='Address State',
        related='address_id.state',
        store=False
    )
    address_phase_id = fields.Many2one(
        string='Address Phase',
        related='address_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_address_ids = fields.One2many(
        comodel_name='clv.summary.address',
        inverse_name='summary_id',
        string='Addresses'
    )
