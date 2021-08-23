# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestReport(models.Model):
    _inherit = 'clv.lab_test.report'

    # person_id = fields.Many2one(
    #     comodel_name='clv.person',
    #     string="Person",
    #     ondelete='restrict'
    # )
    # person_employee_id = fields.Many2one(
    #     comodel_name='hr.employee',
    #     string='Responsible Empĺoyee (Person)',
    #     related='person_id.address_id.employee_id',
    #     store=True
    # )

    # survey_id = fields.Many2one(
    #     comodel_name='survey.survey',
    #     string='Related Survey Type',
    #     related='lab_test_type_id.survey_id',
    #     store=True
    # )

    has_complement = fields.Boolean(string='Has Complement', default=False)

    approved = fields.Boolean(string='Approved', default=False, readonly=True)
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approved by',
        readonly=True
    )
    professional_id = fields.Char(
        comodel_name='hr.employee',
        string='Professional ID',
        related='employee_id.professional_id',
        store=False,
        readonly=True
    )
    date_approved = fields.Date(
        string='Approved Date',
        readonly=True
    )


# class Person(models.Model):
#     _inherit = 'clv.person'

#     lab_test_report_ids = fields.One2many(
#         comodel_name='clv.lab_test.report',
#         inverse_name='person_id',
#         string='Lab Test Reports'
#     )
