# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportPartnerSupplier(models.TransientModel):
    _name = 'import.partner.supplier'

    data = fields.Binary('File', required=True)
    name = fields.Char('file_inputame')
    delimeter = fields.Char('Delimiter', default=',',
                            help='Default delimiter ","')

    '''
        Function to update and correct some values.

        :param values: Dict with the values to import.

        :return Dict with the modified values modifieds.
    '''
    def _update_values(self, values):
        for k, v in values.items():
            if v == 'True':
                values[k] = True
            elif v == 'False':
                values[k] = False

        if values['zip'] and values['country'] == 'ES':
            values['zip'] = values['zip'].zfill(5)

        if values['iban']:
            values['iban'] = values['iban'].replace(' ', '')

        property_values = {
            'fiscal_position': values['fiscal_position'],
            'payment_mode': values['payment_mode'],
            'payment_term': values['payment_term'],
            'currency': values['currency'],
        }
        del values['fiscal_position']
        del values['payment_mode']
        del values['payment_term']
        del values['currency']

        return values, property_values

    def _create_properties(self, partner, props):
        company_list = []
        logging.info("Creating property values")
        if partner.company_id:
            company_list = [partner.company_id.id]
        else:
            company_objs = self.env['res.company'].search([])
            for company_obj in company_objs:
                company_list.append(company_obj.id)
        res_id = 'res.partner,' + str(partner.id)

        for company in company_list:
            if props['fiscal_position']:
                acc_fp = self.env['account.fiscal.position'].search([
                    ('name', '=', props['fiscal_position']),
                    ('company_id', '=', company)
                ])
                if acc_fp:
                    field_name = 'property_account_position_id'
                    fields_obj = self.env['ir.model.fields'].search([
                        ('model', '=', 'res.partner'),
                        ('name', '=', field_name)
                    ])
                    self.env['ir.property'].create({
                        'name': field_name,
                        'res_id': res_id,
                        'fields_id': fields_obj.id,
                        'company_id': company,
                        'value_reference': 'account.fiscal.position,' +
                                           str(acc_fp.id),
                    })
            if partner.customer:
                if props['payment_mode']:
                    cust_pm = self.env['account.payment.mode'].search([
                        ('payment_type', '=', 'inbound'),
                        ('name', '=', props['payment_mode']),
                        ('company_id', '=', company)
                    ])
                    if cust_pm:
                        field_name = 'customer_payment_mode_id'
                        fields_obj = self.env['ir.model.fields'].search([
                            ('model', '=', 'res.partner'),
                            ('name', '=', field_name)
                        ])
                        self.env['ir.property'].create({
                            'name': field_name,
                            'res_id': res_id,
                            'fields_id': fields_obj.id,
                            'company_id': company,
                            'value_reference': 'account.payment.mode,' +
                                               str(cust_pm.id),
                        })
                if props['payment_term']:
                    cust_pt = self.env['account.payment.term'].search([
                        ('name', '=', props['payment_term']),
                        ('company_id', '=', company)
                    ])
                    if cust_pt:
                        field_name = 'property_payment_term_id'
                        fields_obj = self.env['ir.model.fields'].search([
                            ('model', '=', 'res.partner'),
                            ('name', '=', field_name)
                        ])
                        self.env['ir.property'].create({
                            'name': field_name,
                            'res_id': res_id,
                            'fields_id': fields_obj.id,
                            'company_id': company,
                            'value_reference': 'account.payment.term,' +
                                               str(cust_pt.id),
                        })
            if partner.supplier:
                if props['payment_mode']:
                    sup_pm = self.env['account.payment.mode'].search([
                        ('payment_type', '=', 'outbound'),
                        ('name', '=', props['payment_mode']),
                        ('company_id', '=', company)
                    ])
                    if sup_pm:
                        field_name = 'supplier_payment_mode_id'
                        fields_obj = self.env['ir.model.fields'].search([
                            ('model', '=', 'res.partner'),
                            ('name', '=', field_name),
                        ])
                        self.env['ir.property'].create({
                            'name': field_name,
                            'res_id': res_id,
                            'fields_id': fields_obj.id,
                            'company_id': company,
                            'value_reference': 'account.payment.mode,' +
                                               str(sup_pm.id),
                        })
                if props['payment_term']:
                    sup_pt = self.env['account.payment.term'].search([
                        ('name', '=', props['payment_term']),
                        ('company_id', '=', company)
                    ])
                    if sup_pt:
                        field_name = 'property_supplier_payment_term_id'
                        fields_obj = self.env['ir.model.fields'].search([
                            ('model', '=', 'res.partner'),
                            ('name', '=', field_name),
                        ])
                        self.env['ir.property'].create({
                            'name': field_name,
                            'res_id': res_id,
                            'fields_id': fields_obj.id,
                            'company_id': company,
                            'value_reference': 'account.payment.term,' +
                                               str(sup_pt.id),
                        })
                if props['currency']:
                    sup_cu = self.env['res.currency'].search([
                        ('name', '=', props['currency'])
                    ])
                    if sup_cu:
                        field_name = 'property_purchase_currency_id'
                        fields_obj = self.env['ir.model.fields'].search([
                            ('model', '=', 'res.partner'),
                            ('name', '=', field_name)
                        ])
                        self.env['ir.property'].create({
                            'name': field_name,
                            'res_id': res_id,
                            'fields_id': fields_obj.id,
                            'company_id': company,
                            'value_reference': 'res.currency,' +
                                               str(sup_cu.id),
                        })

    '''
        Function to assign not direct mapping data.

        :param values: Dict with the values to import.

        :return Dict with the correct mapping.
    '''
    def _assign_partner_data(self, values):
        partner_data = {}
        bank_info = {}

        # Assign country and state
        if values['country']:
            country_obj = self.env['res.country'].search([(
                'code', '=', values['country'])])
            if country_obj:
                partner_data.update({
                    'country_id': country_obj.id,
                })
        del values['country']

        if values['state']:
            state_obj = self.env[
                'res.country.state'].search([(
                    'name', 'ilike', values['state'])])
            if not state_obj:
                state_obj = state_obj.create({
                    'name': values['state'],
                    'country_id': country_obj.id,
                    'code': values['state'].upper(),
                })

            partner_data.update({
                    'state_id': state_obj[0].id,
            })
        del values['state']

        # Create and assign bank account
        if values['iban']:
            bank_acc_obj = self.env['res.partner.bank'].search([(
                'acc_number', '=', values['iban'])])
            if not bank_acc_obj:
                bank_values = {}
                bank_code = values['iban'][4:8]
                bank_obj = self.env['res.bank'].search([(
                    'code', '=', bank_code)])
                bank_values = {
                    'acc_number': values['iban'],
                }
                if bank_obj:
                    bank_values.update({
                        'bank_id': bank_obj.id,
                    })

                bank_info = bank_values
        del values['iban']

        # Assign category
        if values['category_id']:
            category_obj = self.env['res.partner.category'].search([(
                'name', '=', values['category_id'])])
            if not category_obj:
                category_values = {}
                category_values = {
                    'name': values['category_id'],
                    'active': True,
                }
                category_obj = category_obj.create(category_values)

            partner_data.update({
                'category_id': [(6, 0, [category_obj.id])],
            })

        # Create and assign a contact
        if values['contact_name']:
            contact_obj = self.env[
                'res.partner'].search([
                    ('name', '=', values['contact_name']),
                    ('parent_id', '!=', False)])
            new_contact = True
            if contact_obj:
                for contact in contact_obj:
                    if contact.parent_id.ref == values['ref']:
                        partner_data.update({
                                'child_ids': [(1, contact.id, {
                                    'function': values['contact_function'],
                                    'email': values['contact_email'],
                                    'mobile': values['contact_mobile'],
                                    })],
                            })
                        new_contact = False
                        break
            if new_contact:
                partner_data.update({
                        'child_ids': [(0, 0, {
                            'name': values['contact_name'],
                            'function': values['contact_function'],
                            'email': values['contact_email'],
                            'mobile': values['contact_mobile'],
                            })],
                    })

        del values['contact_name']
        del values['contact_function']
        del values['contact_email']
        del values['contact_mobile']

        if values['language']:
            language_obj = self.env[
                'res.lang'].search([
                    ('iso_code', '=', values['language'])])
            if language_obj:
                partner_data.update({
                    'lang': language_obj.code,
                })

        del values['language']

        return partner_data, bank_info

    '''
        Function to create or write the partner / supplier.

        :param values: Dict with the values to import.
    '''
    def _create_new_partner(self, values, props):
        # Update existing customers
        current_partner = self.env['res.partner'].search([
            ('ref', '=', values['ref'])
        ])
        fields = {}
        bank_info = {}
        fields, bank_info = self._assign_partner_data(values)
        if current_partner:
            current_partner.write(values)
            _logger.info("Updating partner: %s", current_partner.ref)
        else:
            current_partner = current_partner.create(values)
            _logger.info("Creating partner: %s", current_partner.ref)

        current_partner.write(fields)
        self._create_properties(current_partner, props)
        if bank_info:
            if current_partner.company_id:
                cur_company = current_partner.company_id.id
            else:
                cur_company = False
            bank_info.update({
                'partner_id': current_partner.id,
                'company_id': cur_company,
            })
            bank_obj = self.env['res.partner.bank'].create(bank_info)
            current_partner.write({
                'bank_ids': [(6, 0, [bank_obj.id])]
            })

    '''
        Function to read the csv file and convert it to a dict.

        :return Dict with the columns and its value.
    '''
    def action_import(self):
        """Load Inventory data from the CSV file."""
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))
        # Decode the file data
        data = base64.b64decode(self.data).decode('utf-8')
        file_input = StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]

        # Get column names
        keys_init = reader_info[0]
        keys = []
        for k in keys_init:
            temp = k.replace(' ', '_')
            keys.append(temp)
        del reader_info[0]
        values = {}

        for i in range(len(reader_info)):
            # Don't read rows that start with ( or are empty
            if not (reader_info[i][0] is '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                values = dict(zip(keys, field))
                new_values, props = self._update_values(values)
                self._create_new_partner(new_values, props)

        return {'type': 'ir.actions.act_window_close'}
