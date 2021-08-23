# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ExternalSypnTemplateMassEdit(models.TransientModel):
    _description = 'External Sync Template Mas Edit'
    _name = 'clv.external_sync.template.mass_edit'

    def _default_external_sync_template_ids(self):
        return self._context.get('active_ids')
    external_sync_template_ids = fields.Many2many(
        comodel_name='clv.external_sync.template',
        relation='clv_external_sync_template_mass_edit_rel',
        string='External Sync Templates',
        default=_default_external_sync_template_ids
    )

    external_host_id = fields.Many2one(
        comodel_name='clv.external_sync.host',
        string='External Host'
    )
    external_host_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='External Host:', default=False, readonly=False, required=False
    )

    external_disable_identification = fields.Boolean(
        string='Disable Identification'
    )
    external_disable_identification_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Disable Identification:', default=False, readonly=False, required=False
    )

    external_disable_check_missing = fields.Boolean(
        string='Disable Check Missing'
    )
    external_disable_check_missing_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Disable Check Missing:', default=False, readonly=False, required=False
    )

    external_disable_inclusion = fields.Boolean(
        string='Disable Inclusion'
    )
    external_disable_inclusion_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Disable Inclusion:', default=False, readonly=False, required=False
    )

    external_disable_sync = fields.Boolean(
        string='Disable Sync'
    )
    external_disable_sync_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Disable Sync:', default=False, readonly=False, required=False
    )

    external_last_update_start = fields.Datetime(
        string="Last Update (Start)"
    )
    external_last_update_start_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Last Update (Start):', default=False, readonly=False, required=False
    )

    external_last_update_end = fields.Datetime(
        string="Last Update (End)"
    )
    external_last_update_end_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Last Update (End):', default=False, readonly=False, required=False
    )

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_external_sync_template_mass_edit(self):
        self.ensure_one()

        for external_sync_template in self.external_sync_template_ids:

            _logger.info(u'%s %s', '>>>>>', external_sync_template.name)

            if self.external_host_id_selection == 'set':
                external_sync_template.external_host_id = self.external_host_id.id
            if self.external_host_id_selection == 'remove':
                external_sync_template.external_host_id = False

            if self.external_disable_identification_selection == 'set':
                external_sync_template.external_disable_identification = self.external_disable_identification
            if self.external_disable_identification_selection == 'remove':
                external_sync_template.external_disable_identification = False

            if self.external_disable_check_missing_selection == 'set':
                external_sync_template.external_disable_check_missing = self.external_disable_check_missing
            if self.external_disable_check_missing_selection == 'remove':
                external_sync_template.external_disable_check_missing = False

            if self.external_disable_inclusion_selection == 'set':
                external_sync_template.external_disable_inclusion = self.external_disable_inclusion
            if self.external_disable_inclusion_selection == 'remove':
                external_sync_template.external_disable_inclusion = False

            if self.external_disable_sync_selection == 'set':
                external_sync_template.external_disable_sync = self.external_disable_sync
            if self.external_disable_sync_selection == 'remove':
                external_sync_template.external_disable_sync = False

            if self.external_last_update_start_selection == 'set':
                external_sync_template.external_last_update_start = self.external_last_update_start
            if self.external_last_update_start_selection == 'remove':
                external_sync_template.external_last_update_start = False

            if self.external_last_update_end_selection == 'set':
                external_sync_template.external_last_update_end = self.external_last_update_end
            if self.external_last_update_end_selection == 'remove':
                external_sync_template.external_last_update_end = False

        return True
