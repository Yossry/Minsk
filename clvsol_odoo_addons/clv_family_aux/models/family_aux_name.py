# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class FamilyAux(models.Model):
    _inherit = 'clv.family_aux'

    suggested_name = fields.Char(
        string="Suggested Name", required=False, store=True,
        compute="_get_suggested_name",
        help='Suggested Name for the Family (Aux).'
    )
    automatic_set_name = fields.Boolean(
        string='Automatic Name',
        help="If checked, the Family (Aux) Name will be set automatically.",
        default=True
    )

    @api.depends('street', 'street2')
    def _get_suggested_name(self):
        for record in self:
            if record.street:
                address_name = record.street
                if record.street2:
                    address_name = address_name + ' - ' + record.street2
                family_name_format = self.env['ir.config_parameter'].sudo().get_param(
                    'clv.global_settings.current_family_name_format', '').strip()
                family_name = family_name_format.replace('<address_name>', address_name)
                record.suggested_name = family_name
            else:
                record.suggested_name = 'Address Name...'

    @api.model
    def create(self, values):
        record = super().create(values)

        if record.automatic_set_name:
            if record.name != record.suggested_name:
                record['name'] = record.suggested_name

        return record

    @api.multi
    def write(self, values):
        ret = super().write(values)
        for record in self:
            if record.suggested_name is not False:
                if record.automatic_set_name:
                    if record.name != record.suggested_name:
                        values['name'] = record.suggested_name
                        super().write(values)
                else:
                    if ('name' in values and values['name'] == '/') or \
                       (record.name == '/'):
                        values['name'] = record.suggested_name
                        super().write(values)
        return ret
