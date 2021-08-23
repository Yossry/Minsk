# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Phase(models.Model):
    _name = "clv.phase"
    _inherit = 'clv.phase', 'clv.abstract.model.log'

    log_model = fields.Char(string='Log Model Name', required=True, default='clv.global_log')

    log_ids = fields.One2many(
        string='Global Logs',
        comodel_name='clv.global_log',
        compute='_compute_log_ids_and_count',
    )
