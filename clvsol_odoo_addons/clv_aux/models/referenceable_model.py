# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AuxCode(models.Model):
    _name = "clv.aux.code"
    _inherit = 'clv.aux.code', 'clv.abstract.reference'
