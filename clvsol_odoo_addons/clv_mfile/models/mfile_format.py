# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MediaFileFormat(models.Model):
    _description = 'Media File Format'
    _name = 'clv.mfile.format'
    _inherit = 'clv.abstract.format'

    code = fields.Char(string='Format Code', required=False)

    mfile_ids = fields.Many2many(
        comodel_name='clv.mfile',
        relation='clv_mfile_format_rel',
        column1='format_id',
        column2='mfile_id',
        string='Media Files'
    )


class MediaFile(models.Model):
    _inherit = "clv.mfile"

    format_ids = fields.Many2many(
        comodel_name='clv.mfile.format',
        relation='clv_mfile_format_rel',
        column1='mfile_id',
        column2='format_id',
        string='Formats'
    )
    format_names = fields.Char(
        string='Format Names',
        compute='_compute_format_names',
        store=True
    )

    @api.depends('format_ids')
    def _compute_format_names(self):
        for r in self:
            format_names = False
            for format in r.format_ids:
                if format_names is False:
                    format_names = format.name
                else:
                    format_names = format_names + ', ' + format.name
            r.format_names = format_names
