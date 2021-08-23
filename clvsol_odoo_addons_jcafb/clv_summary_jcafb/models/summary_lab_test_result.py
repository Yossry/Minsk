# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryLabTestResult(models.Model):
    _description = 'Summary LabTest Result'
    _name = 'clv.summary.lab_test.result'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    lab_test_result_id = fields.Many2one(
        comodel_name='clv.lab_test.result',
        string='Lab Test Result',
        ondelete='cascade'
    )
    lab_test_request_id = fields.Many2one(
        comodel_name='clv.lab_test.request',
        string='Lab Test Request',
        related='lab_test_result_id.lab_test_request_id',
        store=False
    )
    lab_test_type_id = fields.Many2one(
        comodel_name='clv.lab_test.type',
        string='Lab Test Type',
        related='lab_test_result_id.lab_test_type_id',
        store=False
    )
    lab_test_result_state = fields.Selection(
        string='LabTestResult State',
        related='lab_test_result_id.state',
        store=False
    )
    lab_test_result_phase_id = fields.Many2one(
        string='LabTestResult Phase',
        related='lab_test_result_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_lab_test_result_ids = fields.One2many(
        comodel_name='clv.summary.lab_test.result',
        inverse_name='summary_id',
        string='Lab Test Results'
    )
