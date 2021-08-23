# -*- coding: utf-8 -*-

from odoo import api, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        flag = False
        if self.partner_id.name and self.partner_id.street and \
                self.partner_id.city and self.partner_id.country_id and \
                self.partner_id.nit and self.partner_id.phone and \
                self.partner_id.state_id and self.partner_id.zip and \
                self.partner_id.mobile and self.partner_id.email and \
                self.partner_id.l10n_co_document_type and self.partner_id.dv and \
                self.partner_id.l10n_co_edi_obligation_type_ids and \
                (self.partner_id.l10n_co_edi_large_taxpayer or
                 self.partner_id.l10n_co_edi_simplified_regimen) and \
                self.partner_id.ciiu:
            flag = True

        if not flag:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Open: Vendor'),
                'res_model': 'res.partner.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'active_id': self.id,
                    'active_model': 'purchase.order',
                    'default_partner_id': self.partner_id.id,
                    'default_street': self.partner_id.street,
                    'default_company_type': self.partner_id.company_type,
                    'default_first_name': self.partner_id.first_name,
                    'default_sale_order': self.id,
                    'default_last_name': self.partner_id.last_name,
                    'default_middle_name': self.partner_id.middle_name,
                    'default_second_last_name': self.partner_id.second_last_name,
                    'default_company_name': self.partner_id.company_name,
                    'default_company_nature': self.partner_id.company_nature,
                    'default_is_company': self.partner_id.is_company,
                    'default_name': self.partner_id.name,
                    'default_field_1': self.partner_id.field_1.id,
                    'default_field_2': self.partner_id.field_2,
                    'default_field_3': self.partner_id.field_3,
                    'default_field_4': self.partner_id.field_4.id,
                    'default_field_5': self.partner_id.field_5,
                    'default_field_6': self.partner_id.field_6,
                    'default_field_7': self.partner_id.field_7.id,
                    'default_field_8': self.partner_id.field_8,
                    'default_field_9': self.partner_id.field_9.id,
                    'default_field_10': self.partner_id.field_10,
                    'default_field_11': self.partner_id.field_11.id,
                    'default_field_12': self.partner_id.field_12,
                    'default_city': self.partner_id.city,
                    'default_state_id': self.partner_id.state_id.id,
                    'default_zip': self.partner_id.zip,
                    'default_country_id': self.partner_id.country_id.id,
                    'default_phone': self.partner_id.phone,
                    'default_mobile': self.partner_id.mobile,
                    'default_email': self.partner_id.email,
                    'default_nit': self.partner_id.nit,
                    'default_dv': self.partner_id.dv,
                    'default_l10n_co_edi_obligation_type_ids': self.partner_id.l10n_co_edi_obligation_type_ids.ids,
                    'default_l10n_co_edi_large_taxpayer': self.partner_id.l10n_co_edi_large_taxpayer,
                    'default_l10n_co_edi_simplified_regimen': self.partner_id.l10n_co_edi_simplified_regimen,
                    'default_ciiu': self.partner_id.ciiu.ids,
                    'default_l10n_co_document_type': self.partner_id.l10n_co_document_type,
                }
            }
        else:
            return super(PurchaseOrder, self).button_confirm()
