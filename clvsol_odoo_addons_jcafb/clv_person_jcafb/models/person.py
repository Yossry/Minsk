# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Person(models.Model):
    _name = "clv.person"
    _inherit = 'clv.person', 'clv.abstract.random'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsible Empĺoyee',
        related='ref_address_id.employee_id',
        store=True
    )


class PersonHistory(models.Model):
    _inherit = 'clv.person.history'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsible Empĺoyee',
        required=False,
        readonly=False
    )
