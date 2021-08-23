# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressLabTestRequestSetup(models.TransientModel):
    _description = 'Address Lab Test Request Setup'
    _name = 'clv.address.lab_test.request.setup'

    def _default_address_ids(self):
        return self._context.get('active_ids')
    address_ids = fields.Many2many(
        comodel_name='clv.address',
        relation='clv_address_address_lab_test_request_setup_rel',
        string='Addresses',
        default=_default_address_ids
    )

    lab_test_type_ids = fields.Many2many(
        comodel_name='clv.lab_test.type',
        relation='clv_lab_test_type_address_lab_test_request_setup_rel',
        string='Lab Test Types'
    )

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
    def do_address_lab_test_request_setup(self):
        self.ensure_one()

        LabTestRequest = self.env['clv.lab_test.request']

        for address in self.address_ids:

            _logger.info(u'%s %s', '>>>>>', address.name)

            for lab_test_type in self.lab_test_type_ids:
                m2m_list = []
                m2m_list.append((4, lab_test_type.id))

                ref_id = address._name + ',' + str(address.id)

                _logger.info(u'%s %s %s', '>>>>>>>>>>', ref_id, m2m_list)

                values = {
                    'code_sequence': 'clv.lab_test.request.code',
                    'lab_test_type_ids': m2m_list,
                    'ref_id': ref_id,
                    'phase_id': self.phase_id.id,
                }
                lab_test_request = LabTestRequest.create(values)

                _logger.info(u'%s %s', '>>>>>>>>>>', lab_test_request.code)

        return True
