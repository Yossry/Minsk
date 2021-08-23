# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ExternalSync(models.Model):
    _description = 'External Sync'
    _name = 'clv.external_sync'
    _inherit = 'clv.abstract.external_sync'
    _order = "id desc"

    model = fields.Char(string='Model Name', required=True)
    res_id = fields.Integer(string='Record ID', help="ID of the target record in the database")
    res_last_update = fields.Datetime(string="Record Last Update")
    reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=True)
    reference_name = fields.Char(string='Reference Name', compute='_compute_reference', readonly=True, store=True)

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for record in self:
            if record.model is not False and record.res_id > 0:
                record.reference = "%s,%s" % (record.model, record.res_id)
                Model = self.env[record.model]
                rec = Model.search([
                    ('id', '=', record.res_id),
                ])
                record.reference_name = rec.name_get()[0][1]
