# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    family_aux_ids = fields.One2many(
        comodel_name='clv.family_aux',
        inverse_name='phase_id',
        string='Families (Aux)',
        readonly=True
    )
    count_families_aux = fields.Integer(
        string='Families (Aux) (count)',
        compute='_compute_family_aux_ids_and_count',
    )

    @api.multi
    def _compute_family_aux_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            families_aux = self.env['clv.family_aux'].search(search_domain)

            record.count_families_aux = len(families_aux)
            record.family_aux_ids = [(6, 0, families_aux.ids)]


class FamilyAux(models.Model):
    _inherit = 'clv.family_aux'

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
