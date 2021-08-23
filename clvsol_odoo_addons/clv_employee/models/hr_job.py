# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    active = fields.Boolean(string='Active', default=True)
