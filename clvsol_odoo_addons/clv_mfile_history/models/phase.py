# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    mfile_ids = fields.One2many(
        comodel_name='clv.mfile',
        inverse_name='phase_id',
        string='Media Files',
        readonly=True
    )
    count_mfiles = fields.Integer(
        string='Media Files (count)',
        compute='_compute_mfile_ids_and_count',
    )

    @api.multi
    def _compute_mfile_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            mfiles = self.env['clv.mfile'].search(search_domain)

            record.count_mfiles = len(mfiles)
            record.mfile_ids = [(6, 0, mfiles.ids)]


class Document(models.Model):
    _inherit = 'clv.mfile'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )
