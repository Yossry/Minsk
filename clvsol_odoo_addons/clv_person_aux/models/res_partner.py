# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[
        ('clv.person_aux', 'Person (Aux)'),
    ])

    person_aux_ids = fields.One2many(
        string='Related Persons (Aux)',
        comodel_name='clv.person_aux',
        compute='_compute_person_aux_ids_and_count',
    )
    count_persons_aux = fields.Integer(
        compute='_compute_person_aux_ids_and_count',
    )

    @api.multi
    def _get_clv_entity(self):
        self.ensure_one()
        if self.type and self.type[:3] == 'clv':
            return self.env[self.type].search([
                ('partner_id', '=', self.id),
            ])

    @api.multi
    def _compute_person_aux_ids_and_count(self):
        for record in self:
            persons_aux = self.env['clv.person_aux'].search([
                ('partner_id', 'child_of', record.id),
            ])
            record.count_persons_aux = len(persons_aux)
            record.person_aux_ids = [(6, 0, persons_aux.ids)]

    # @api.model
    # def create(self, vals):
    #     """ It overrides create to bind appropriate clv entity. """
    #     if all((
    #         vals.get('type', '').startswith('clv.'),
    #         not self.env.context.get('clv_entity_no_create'),
    #     )):
    #         model = self.env[vals['type']].with_context(
    #             clv_entity_no_create=True,
    #         )
    #         clv_entity = model.create(vals)
    #         return clv_entity.partner_id
    #     return super().create(vals)
