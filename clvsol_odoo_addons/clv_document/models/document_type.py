# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Documentype (models.Model):
    _description = 'Document Type'
    _name = 'clv.document.type'
    _order = 'name'

    name = fields.Char(string='Document Type', required=True)
    code = fields.Char(string='Document Type Code')

    description = fields.Char(string='Document Type Description')

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),

        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]


class Document(models.Model):
    _inherit = "clv.document"

    document_type_id = fields.Many2one(
        comodel_name='clv.document.type',
        string='Document Type',
        ondelete='restrict'
    )

    document_type_description = fields.Char(
        string='Document Type Description',
        related='document_type_id.description',
        store=False
    )
