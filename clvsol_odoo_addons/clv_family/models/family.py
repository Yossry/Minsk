# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.modules import get_module_resource

_logger = logging.getLogger(__name__)


class Family(models.Model):

    _name = 'clv.family'
    _description = 'Family'
    _inherit = 'clv.abstract.partner_entity'

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for record in self:
            if record.code:
                result.append(
                    (record.id,
                     u'%s [%s]' % (record.name, record.code)
                     ))
            else:
                result.append(
                    (record.id,
                     u'%s' % (record.name)
                     ))
        return result

    code = fields.Char(string='Family Code', required=False)

    notes = fields.Text(string='Notes:')

    @api.model
    def _create_vals(self, vals):
        vals = super()._create_vals(vals)
        vals.update({
            'customer': True,
        })
        vals.update({
            'type': self._name,
        })
        return vals

    @api.model_cr_context
    def _get_default_image_path(self, vals):
        res = super()._get_default_image_path(vals)
        if res:
            return res
        image_path = get_module_resource(
            'clv_family', 'static/src/img', 'family-avatar.png',
        )
        return image_path

    @api.multi
    def write(self, values):
        ret = super().write(values)
        for record in self:
            if ('code' in values):
                if record.entity_code != values['code']:
                    vals = {}
                    vals['entity_code'] = values['code']
                    super().write(vals)
        return ret

    @api.multi
    def do_family_clear_address_data(self):

        for address_aux in self:

            # _logger.info(u'>>>>> %s', address_aux.ref_address_id)

            # if (address_aux.reg_state in ['draft', 'revised']):

            data_values = {}

            data_values['street'] = False
            data_values['street2'] = False
            data_values['zip'] = False
            data_values['city'] = False
            data_values['state_id'] = False
            data_values['country_id'] = False
            # data_values['phone'] = False
            # data_values['mobile'] = False

            _logger.info(u'>>>>>>>>>> %s', data_values)

            address_aux.write(data_values)
