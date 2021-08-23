# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    address_aux_ids = fields.One2many(
        comodel_name='clv.address_aux',
        inverse_name='phase_id',
        string='Addresses (Aux)',
        readonly=True
    )
    count_addresses_aux = fields.Integer(
        string='Addresses (Aux) (count)',
        compute='_compute_address_aux_ids_and_count',
    )

    @api.multi
    def _compute_address_aux_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            addresses_aux = self.env['clv.address_aux'].search(search_domain)

            record.count_addresses_aux = len(addresses_aux)
            record.address_aux_ids = [(6, 0, addresses_aux.ids)]


class AddressAux(models.Model):
    _inherit = 'clv.address_aux'

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
