# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryFamily(models.Model):
    _description = 'Summary Family'
    _name = 'clv.summary.family'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    family_id = fields.Many2one(
        comodel_name='clv.family',
        string='Family',
        ondelete='cascade'
    )
    family_global_tag_ids = fields.Many2many(
        string='Family Global Tags',
        related='family_id.global_tag_ids',
        store=False
    )
    family_category_ids = fields.Many2many(
        string='Family Categories',
        related='family_id.category_ids',
        store=False
    )
    family_state = fields.Selection(
        string='Family State',
        related='family_id.state',
        store=False
    )
    family_phase_id = fields.Many2one(
        string='Family Phase',
        related='family_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_family_ids = fields.One2many(
        comodel_name='clv.summary.family',
        inverse_name='summary_id',
        string='Families'
    )
