# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy

from datetime import *

from odoo import api, fields, models


class AbstractLog(models.AbstractModel):
    _description = 'Abstract Log'
    _name = 'clv.abstract.log'
    _order = "id desc"

    model = fields.Char(string='Model Name', required=True)
    res_id = fields.Integer(string='Record ID', help="ID of the target record in the database")
    reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=True)

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for record in self:
            record.reference = "%s,%s" % (record.model, record.res_id)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    date_log = fields.Datetime(
        string='When',
        required=True,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    values = fields.Text(string='Values')
    action = fields.Char(string='Action')
    notes = fields.Text(string='Notes')


class AbstractModelLog(models.AbstractModel):
    _description = 'Abstract Model Log'
    _name = 'clv.abstract.model.log'

    # reference = fields.Char(string='Reference', compute='_compute_object_reference', store=False)

    object_model = fields.Char(string='Object Model', compute='_compute_object_reference', store=False)
    object_res_id = fields.Char(string='Object Record ID', compute='_compute_object_reference', store=False)
    object_reference = fields.Char(string='Object Reference', compute='_compute_object_reference', store=False)

    def _compute_object_reference(self):
        for record in self:
            record.object_model = record._name
            record.object_res_id = record.id
            record.object_reference = "%s,%s" % (record._name, record.id)

    active_log = fields.Boolean(
        string='Active Log',
        help="If unchecked, it will allow you to disable the log without removing it.",
        default=True
    )

    log_model = fields.Char(string='Log Model Name', required=True, readonly=False)

    log_ids = fields.One2many(
        string='Abstract Logs',
        comodel_name='clv.abstract.log',
        compute='_compute_log_ids_and_count',
    )

    count_logs = fields.Integer(
        compute='_compute_log_ids_and_count',
    )

    @api.multi
    def _compute_log_ids_and_count(self):
        for record in self:
            try:
                logs = self.env[record.log_model].search([
                    ('reference', '=', record.object_reference),
                ])
                record.count_logs = len(logs)
                record.log_ids = [(6, 0, logs.ids)]
            except Exception:
                pass

    @api.depends('model', 'res_id')
    def insert_object_log(self, log_model, model, res_id, values, action, notes):
        for record in self:
            if record.active_log or 'active_log' in values:
                values_copy = values.copy()
                if 'image_small' in values_copy:
                    values_copy['image_small'] = '<image_small>'
                if 'image_medium' in values_copy:
                    values_copy['image_medium'] = '<image_medium>'
                if 'image' in values_copy:
                    values_copy['image'] = '<image>'
                vals = {
                    'model': model,
                    'res_id': res_id,
                    'values': values_copy,
                    'action': action,
                    'notes': notes,
                }
                record.env[log_model].create(vals)

    @api.multi
    def write(self, values):
        action = 'write'
        notes = False
        for record in self:
            record.insert_object_log(record.log_model, record._name, record.id, values, action, notes)
        return super().write(values)

    @api.model
    def create(self, values):
        action = 'create'
        notes = False
        record = super().create(values)
        record.insert_object_log(record.log_model, record._name, record.id, values, action, notes)
        return record
