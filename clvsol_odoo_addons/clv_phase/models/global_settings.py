# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [
    ("current_phase_id", "clv.global_settings.current_phase_id"),
]


class GlobalSettings(models.TransientModel):
    _inherit = 'clv.global_settings'

    current_phase_id = fields.Char(
        string='Phase',
        compute='_compute_current_phase_id',
        store=False,
    )

    @api.multi
    def set_values(self):
        self.ensure_one()

        super().set_values()

        for field_name, key_name in PARAMS:
            value = str(getattr(self, field_name, '')).strip()
            self.env['ir.config_parameter'].set_param(key_name, value)

    def get_values(self):

        res = super().get_values()

        for field_name, key_name in PARAMS:
            res[field_name] = self.env['ir.config_parameter'].get_param(key_name, '').strip()
        return res


class GlobalSettings_2(models.TransientModel):
    _inherit = 'clv.global_settings'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase:',
        ondelete='restrict',
    )

    @api.depends('phase_id')
    def _compute_current_phase_id(self):
        for r in self:
            r.current_phase_id = r.phase_id.id

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        Phase = self.env['clv.phase']

        current_phase_id = False
        try:
            if defaults['current_phase_id'] != '' and \
               defaults['current_phase_id'] != 'False':
                current_phase_id = defaults['current_phase_id']
        except KeyError:
            pass

        phase = Phase.search([
            ('id', '=', current_phase_id),
        ])
        defaults['phase_id'] = phase.id

        return defaults
