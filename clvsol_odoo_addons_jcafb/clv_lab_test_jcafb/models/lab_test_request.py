# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestRequest(models.Model):
    _inherit = 'clv.lab_test.request'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Received by'
    )
    date_received = fields.Datetime(string='Received Date')

    # document_id = fields.Many2one(
    #     comodel_name='clv.document',
    #     string='Related Document'
    # )
    # survey_user_input_id = fields.Many2one(
    #     comodel_name='survey.user_input',
    #     string='Related Survey User Input',
    #     related='document_id.survey_user_input_id',
    #     store=False,
    #     readonly=True
    # )
