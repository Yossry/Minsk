# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import *

from odoo import api, models, fields


class MediaFile(models.Model):
    _description = 'Media File'
    _name = 'clv.mfile'
    _order = 'name'

    name = fields.Char('Name', required=True, translate=False)
    alias = fields.Char('Alias', help='Common name that the file is referred')

    code = fields.Char(string='Code', required=False)

    path = fields.Char(string='Path', compute='_compute_path_str', store=False, readonly=True)
    description = fields.Text(string='Description', translate=False)
    notes = fields.Text(string='Notes')
    date_inclusion = fields.Datetime(
        'Inclusion Date',
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    url = fields.Char('URL', help="URL of the File")

    parent_id = fields.Many2one('clv.mfile', 'Parent File')
    child_ids = fields.One2many('clv.mfile', 'parent_id', 'Child Files')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE(code)',
         u'Error! The Media File Code must be unique!'
         )
    ]

    @api.one
    def _compute_path_str(self):
        if self.code:
            if self.alias:
                self.path = self.alias
            else:
                self.path = self.code
