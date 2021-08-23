# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ReferenceableModel(models.Model):
    _description = 'Referenceable Model'
    _name = 'clv.referenceable.model'
    _order = 'priority, name'

    base_model = fields.Char(string='Base Model', required=True)
    name = fields.Char(string='Name', required=True, translate=True)
    model = fields.Char(string='Referenceable Model', required=True)
    priority = fields.Integer(string='Priority', default=10)


class AbstractReference(models.AbstractModel):
    _description = 'Abstract Reference'
    _name = 'clv.abstract.reference'

    @api.model
    def referenceable_models(self):
        return [(ref.model, ref.name) for ref in self.env['clv.referenceable.model'].search([
            ('base_model', '=', self._name),
        ])]

    ref_id = fields.Reference(
        selection='referenceable_models',
        string='Refers to')
    ref_model = fields.Char(
        string='Refers to (Model)',
        compute='_compute_refenceable_model',
        store=True
    )
    ref_name = fields.Char(
        string='Refers to (Name)',
        compute='_compute_refenceable_model',
        store=True
    )
    ref_code = fields.Char(
        string='Refers to (Code)',
        compute='_compute_refenceable_model',
        store=True
    )
    ref_suport = fields.Char(
        string='Refers to (Suport)',
        compute='_compute_ref_suport',
        store=False
    )

    @api.depends('ref_id')
    def _compute_refenceable_model(self):
        for record in self:
            try:
                if record.ref_id:
                    record.ref_model = record.ref_id._name
                    record.ref_name = record.ref_id.name
                    record.ref_code = record.ref_id.code
            except Exception:
                record.ref_model = False
                record.ref_name = False
                record.ref_code = False

    @api.multi
    def _compute_ref_suport(self):
        for record in self:
            if record.ref_id is not False:
                ref_name = record.ref_id.name
                ref_code = record.ref_id.code
                record.ref_suport = record.ref_id._name + ',' + str(record.ref_id.id)
                if record.ref_name is False or record.ref_name != ref_name or \
                   record.ref_code is False or record.ref_code != ref_code:
                    record = self.env[self._name].search([('id', '=', record.id)])
                    record.write({'ref_id': record.ref_suport})
