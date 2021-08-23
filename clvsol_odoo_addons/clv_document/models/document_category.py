# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class DocumentCategory(models.Model):
    _description = 'Document Category'
    _name = 'clv.document.category'
    _inherit = 'clv.abstract.category'

    code = fields.Char(string='Category Code', required=False)

    parent_id = fields.Many2one(
        comodel_name='clv.document.category',
        string='Parent Category',
        index=True,
        ondelete='restrict'
    )

    child_ids = fields.One2many(
        comodel_name='clv.document.category',
        inverse_name='parent_id',
        string='Child Categories'
    )

    document_ids = fields.Many2many(
        comodel_name='clv.document',
        relation='clv_document_category_rel',
        column1='category_id',
        column2='document_id',
        string='Documents'
    )

    document_type_ids = fields.Many2many(
        comodel_name='clv.document.type',
        relation='clv_document_type_category_rel',
        column1='category_id',
        column2='document_type_id',
        string='Document Types'
    )

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]


class Document(models.Model):
    _inherit = "clv.document"

    category_ids = fields.Many2many(
        comodel_name='clv.document.category',
        relation='clv_document_category_rel',
        column1='document_id',
        column2='category_id',
        string='Categories'
    )
    category_names = fields.Char(
        string='Category Names',
        compute='_compute_category_names',
        store=True
    )
    category_names_suport = fields.Char(
        string='Category Names Suport',
        compute='_compute_category_names_suport',
        store=False
    )

    @api.depends('category_ids')
    def _compute_category_names(self):
        for r in self:
            r.category_names = r.category_names_suport

    @api.multi
    def _compute_category_names_suport(self):
        for r in self:
            category_names = False
            for category in r.category_ids:
                if category_names is False:
                    category_names = category.complete_name
                else:
                    category_names = category_names + ', ' + category.complete_name
            r.category_names_suport = category_names
            if r.category_names != category_names:
                record = self.env['clv.document'].search([('id', '=', r.id)])
                record.write({'category_ids': r.category_ids})


class DocumentType(models.Model):
    _inherit = "clv.document.type"

    category_ids = fields.Many2many(
        comodel_name='clv.document.category',
        relation='clv_document_type_category_rel',
        column1='document_type_id',
        column2='category_id',
        string='Categories'
    )
    category_names = fields.Char(
        string='Category Names',
        compute='_compute_category_names',
        store=True
    )
    category_names_suport = fields.Char(
        string='Category Names Suport',
        compute='_compute_category_names_suport',
        store=False
    )

    @api.depends('category_ids')
    def _compute_category_names(self):
        for r in self:
            r.category_names = r.category_names_suport

    @api.multi
    def _compute_category_names_suport(self):
        for r in self:
            category_names = False
            for category in r.category_ids:
                if category_names is False:
                    category_names = category.complete_name
                else:
                    category_names = category_names + ', ' + category.complete_name
            r.category_names_suport = category_names
            if r.category_names != category_names:
                record = self.env['clv.document.type'].search([('id', '=', r.id)])
                record.write({'category_ids': r.category_ids})
