# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    person_aux_ids = fields.One2many(
        comodel_name='clv.person_aux',
        inverse_name='phase_id',
        string='Persons (Aux)',
        readonly=True
    )
    count_persons_aux = fields.Integer(
        string='Persons (Aux) (count)',
        compute='_compute_person_aux_ids_and_count',
    )

    @api.multi
    def _compute_person_aux_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            persons_aux = self.env['clv.person_aux'].search(search_domain)

            record.count_persons_aux = len(persons_aux)
            record.person_aux_ids = [(6, 0, persons_aux.ids)]


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    def _default_phase_id(self):
        phase_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_phase_id', '').strip())
        return phase_id
    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        default=_default_phase_id,
        ondelete='restrict'
    )
