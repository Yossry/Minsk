# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models


class Summary(models.Model):
    _description = 'Summary'
    _name = 'clv.summary'
    _order = "reference_name"
    _rec_name = 'reference_name'

    model = fields.Char(string='Model Name ', required=True)
    res_id = fields.Integer(
        string='Record ID',
        help="ID of the target record in the database",
        required=True
    )
    res_last_update = fields.Datetime(string="Record Last Update")
    reference = fields.Char(
        string='Reference ',
        compute='_compute_reference',
        readonly=True,
        store=True
    )
    reference_name = fields.Char(
        string='Reference Name',
        compute='_compute_reference',
        readonly=True,
        store=True
    )

    date_summary = fields.Datetime(
        string='Summary Date', required=False, readonly=False,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    notes = fields.Text(string='Notes')

    action = fields.Char(
        string='Action',
        required=False,
        help="Name of the action used to process the summary."
    )

    active = fields.Boolean(string='Active', default=1)

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for record in self:
            if (record.model is not False) and (record.res_id != 0):
                record.reference = "%s,%s" % (record.model, record.res_id)
                Model = self.env[record.model]
                rec = Model.search([
                    ('id', '=', record.res_id),
                ])
                record.reference_name = rec.name_get()[0][1]
