# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ModelExportTemplateDocumentItem(models.Model):
    _description = 'Model Export Template Document Item'
    _name = "clv.model_export.template.document_item"
    _order = "sequence"

    name = fields.Char(string='Alias', index=False, required=False)

    model_export_template_id = fields.Many2one(
        comodel_name='clv.model_export.template',
        string='Model Export Template',
        ondelete='restrict'
    )

    document_item_id = fields.Many2one(
        comodel_name='clv.document.item',
        string='Document Item',
        ondelete='restrict',
        domain="[('document_type_id','!=','False')]"
    )
    document_item_code = fields.Char(
        string='Item Code',
        related='document_item_id.code',
        store=False
    )
    document_item_document_type_id = fields.Many2one(
        string='Item Type',
        related='document_item_id.document_type_id',
        store=True
    )
    document_item_name = fields.Char(
        string='Item',
        related='document_item_id.name',
        store=False
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    model_export_display = fields.Boolean(string='Display in Export', default=True)


class ModelExportTemplate(models.Model):
    _inherit = 'clv.model_export.template'

    use_document_items = fields.Boolean(string='Use Document Items', default=False)

    model_export_template_document_item_ids = fields.One2many(
        comodel_name='clv.model_export.template.document_item',
        inverse_name='model_export_template_id',
        string='Model Export Template Document Items'
    )

    count_model_export_template_document_items = fields.Integer(
        string='Model Export Template Document Items (count)',
        compute='_compute_count_model_export_template_document_item',
        store=True
    )

    @api.depends('model_export_template_document_item_ids')
    def _compute_count_model_export_template_document_item(self):
        for r in self:
            r.count_model_export_template_document_items = len(r.model_export_template_document_item_ids)
