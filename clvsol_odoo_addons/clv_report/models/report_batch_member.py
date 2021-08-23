# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ReportBatchMember(models.Model):
    _description = 'Report Batch Member'
    _name = 'clv.report.batch.member'
    _order = "sequence"

    report_batch_id = fields.Many2one(
        comodel_name='clv.report.batch',
        string='Report Batch ',
        required=False
    )

    notes = fields.Text(string='Notes')

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )


class ReportBatch(models.Model):
    _inherit = 'clv.report.batch'

    report_batch_member_ids = fields.One2many(
        comodel_name='clv.report.batch.member',
        inverse_name='report_batch_id',
        string='Members',
        readonly=False
    )
    count_report_batch_members = fields.Integer(
        string='Members (count)',
        compute='_compute_count_report_batch_members',
        store=False
    )

    @api.depends('report_batch_member_ids')
    def _compute_count_report_batch_members(self):
        for r in self:
            r.count_report_batch_members = len(r.report_batch_member_ids)
