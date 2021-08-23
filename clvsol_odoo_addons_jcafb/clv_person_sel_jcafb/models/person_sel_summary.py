# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PersonSelSummary(models.Model):
    _description = 'Person Selection Summary'
    _name = 'clv.person_sel.summary'
    _inherit = 'clv.abstract.row'
    _order = 'name'
