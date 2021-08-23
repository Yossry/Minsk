# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ModelExportLabTestCriterion(models.Model):
    _description = 'Model Export Lab Test Criterion'
    _name = "clv.model_export.lab_test_criterion"
    _order = "sequence"

    name = fields.Char(string='Alias', index=False, required=False)

    model_export_id = fields.Many2one(
        comodel_name='clv.model_export',
        string='Model Export',
        ondelete='restrict'
    )

    lab_test_criterion_id = fields.Many2one(
        comodel_name='clv.lab_test.criterion',
        string='Lab Test Criterion',
        ondelete='restrict',
        domain="[('lab_test_type_id','!=','False')]"
    )
    lab_test_criterion_code = fields.Char(
        string='Item Code',
        related='lab_test_criterion_id.code',
        store=False
    )
    lab_test_criterion_lab_test_type_id = fields.Many2one(
        string='Item Type',
        related='lab_test_criterion_id.lab_test_type_id',
        store=True
    )
    lab_test_criterion_name = fields.Char(
        string='Item',
        related='lab_test_criterion_id.name',
        store=False
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    model_export_display = fields.Boolean(string='Display in Export', default=True)


class ModelExport(models.Model):
    _inherit = 'clv.model_export'

    use_lab_test_criteria = fields.Boolean(string='Use Lab Test Criteria', default=False)

    model_export_lab_test_criterion_ids = fields.One2many(
        comodel_name='clv.model_export.lab_test_criterion',
        inverse_name='model_export_id',
        string='Model Export Lab Test Criteria'
    )

    count_model_export_lab_test_criteria = fields.Integer(
        string='Model Export Lab Test Criteria (count)',
        compute='_compute_count_model_export_lab_test_criterion',
        store=True
    )

    @api.depends('model_export_lab_test_criterion_ids')
    def _compute_count_model_export_lab_test_criterion(self):
        for r in self:
            r.count_model_export_lab_test_criteria = len(r.model_export_lab_test_criterion_ids)
