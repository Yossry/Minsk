# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = 'clv.patient'

    document_ids = fields.One2many(
        string='Documents',
        comodel_name='clv.document',
        compute='_compute_document_ids_and_count',
    )
    count_documents = fields.Integer(
        string='Documents',
        compute='_compute_document_ids_and_count',
    )

    @api.multi
    def _compute_document_ids_and_count(self):
        for record in self:
            documents = self.env['clv.document'].search([
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ])
            record.count_documents = len(documents)
            record.document_ids = [(6, 0, documents.ids)]
