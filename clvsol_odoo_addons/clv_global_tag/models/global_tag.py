# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GlobalTag(models.Model):
    _description = 'Global Tag'
    _name = 'clv.global_tag'
    _inherit = 'clv.abstract.tag'

    parent_id = fields.Many2one(
        comodel_name='clv.global_tag',
        string='Parent Tag',
        index=True,
        ondelete='restrict'
    )

    child_ids = fields.One2many(
        comodel_name='clv.global_tag',
        inverse_name='parent_id',
        string='Child Tags'
    )
