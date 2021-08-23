# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SummaryLabTestRequest(models.Model):
    _description = 'Summary LabTest Request'
    _name = 'clv.summary.lab_test.request'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    lab_test_request_id = fields.Many2one(
        comodel_name='clv.lab_test.request',
        string='Lab Test Request',
        ondelete='cascade'
    )
    lab_test_type_ids = fields.Many2many(
        comodel_name='clv.lab_test.type',
        string='Lab Test Types',
        related='lab_test_request_id.lab_test_type_ids',
        store=False
    )
    lab_test_type_names = fields.Char(
        string='Category Names Suport',
        compute='_compute_lab_test_type_names',
        store=False
    )
    lab_test_request_state = fields.Selection(
        string='LabTestRequest State',
        related='lab_test_request_id.state',
        store=False
    )
    lab_test_request_phase_id = fields.Many2one(
        string='LabTestRequest Phase',
        related='lab_test_request_id.phase_id',
        store=False
    )

    @api.multi
    def _compute_lab_test_type_names(self):
        for r in self:
            lab_test_type_names = False
            for lab_test_type in r.lab_test_type_ids:
                if lab_test_type_names is False:
                    lab_test_type_names = lab_test_type.name
                else:
                    lab_test_type_names = lab_test_type_names + ', ' + lab_test_type.name
            r.lab_test_type_names = lab_test_type_names
            if r.lab_test_type_names != lab_test_type_names:
                record = self.env['clv.address'].search([('id', '=', r.id)])
                record.write({'lab_test_type_ids': r.lab_test_type_ids})


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_lab_test_request_ids = fields.One2many(
        comodel_name='clv.summary.lab_test.request',
        inverse_name='summary_id',
        string='Lab Test Requests'
    )
