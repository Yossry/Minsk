# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MediaFileAnotation(models.Model):
    _description = 'Media File Annotation'
    _name = 'clv.mfile.annotation'
    _inherit = 'clv.object.annotation', 'clv.code.model'

    code = fields.Char(string='Annotation Code', required=False)
    code_sequence = fields.Char(default='clv.annotation.code')

    mfile_id = fields.Many2one(
        comodel_name='clv.mfile',
        string='Media File',
        ondelete='cascade'
    )

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]


class MediaFile(models.Model):
    _inherit = "clv.mfile"

    annotation_ids = fields.One2many(
        comodel_name='clv.mfile.annotation',
        inverse_name='mfile_id',
        string='Annotations'
    )
