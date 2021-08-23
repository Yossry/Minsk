# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportOpeningJournal(models.TransientModel):
    _name = 'import.opening.journal'

    data = fields.Binary(string='File', required=True)
    name = fields.Char(string='Filename')
    delimeter = fields.Char(
        string='Delimiter',
        default=',',
        help='Default delimiter ","',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True
    )

    '''
        Function to update and correct some values.

        :param values: Dict with the values to import.

        :return Dict with the modified values modifieds.
    '''
    def _update_values(self, values):
        if values['debit']:
            values['debit'] = values['debit'].replace('.', '')
            values['debit'] = values['debit'].replace(',', '.')

        if values['credit']:
            values['credit'] = values['credit'].replace('.', '')
            values['credit'] = values['credit'].replace(',', '.')

        values.update({
            'debit': float(values['debit']) if values['debit'] else 0.00,
            'credit': float(values['credit']) if values['credit'] else 0.00,
        })
        if values['debit'] < 0:
            values['credit'] = abs(values['debit'])
            values['debit'] = 0.00

        if values['credit'] < 0:
            values['debit'] = abs(values['credit'])
            values['credit'] = 0.00

        values['move_id'] = int(values['move_id'])
        return values

    '''
        Function to assign not direct mapping data.

        :param values: Dict with the values to import.

        :return Dict with the correct mapping.
    '''
    def _assign_product_data(self, values):
        # Search for the account
        if values['account']:
            if values['account'][:2] in ('40', '41', '43'):
                if values['credit']:
                    pending_obj = self.env['pending.effects.tmp'].search([
                        ('account', '=', values['account']),
                        ('credit', '=', values['credit']),
                        ('used', '=', False),
                    ])
                if values['debit']:
                    pending_obj = self.env['pending.effects.tmp'].search([
                        ('account', '=', values['account']),
                        ('debit', '=', values['debit']),
                        ('used', '=', False),
                    ])
                if values['account'][:6] == '410004':
                    code = '410400'
                elif values['account'][:6] == '410009':
                    code = '410900'
                else:
                    code = values['account'][:2].ljust(6, '0')
                partner_obj = self.env['res.partner'].search([
                    ('ref', '=', values['account'])
                ])
                if pending_obj:
                    values.update({
                        'pending': pending_obj[0].id,
                    })
                if partner_obj:
                    values.update({
                        'partner_id': partner_obj[0].id
                    })
                values['account'] = code
            else:
                first = False
                if len(values['account']) < 6:
                    values['account'] = values['account'].ljust(6, '0')
                else:
                    max_len = len(values['account'])
                    for digit in range(0, max_len):
                        if values['account'][digit] == '0':
                            if first:
                                last = 6 - first
                                new_code = values['account'][:digit-1] + \
                                    values['account'][-last:]
                                values['account'] = new_code
                                break
                            first = digit
                        else:
                            first = False
            account_obj = self.env['account.account'].search([
                ('code', '=', values['account']),
                ('company_id', '=', self.company_id.id),
            ])
            if account_obj:
                values.update({
                    'account_id': account_obj.id,
                })
        del values['account']

        if values['analytic_account_id']:
            an_obj = self.env['account.analytic.account'].search([
                ('name', '=', values['analytic_account_id'])
            ])
            values['analytic_account_id'] = an_obj.id

        return values

    '''
        Function to create the opening journal lines.

        :param values: Dict with the values to import.
    '''
    def _create_new_opening_journal(self, values, i):
        values = self._assign_product_data(values)
        acc_move_obj = self.env['account.move'].search([
            ('name', '=', values['move_id'])
        ])
        if not acc_move_obj:
            journal_obj = self.env['account.journal'].search([
                ('code', '=', 'HIST')
            ])
            acc_move_obj = acc_move_obj.create({
                'journal_id': journal_obj.id,
                'ref': values['move_id'],
                'name': values['move_id'],
                'date': values['m_date']
                })
        del values['m_date']
        values['move_id'] = acc_move_obj.id

        op_ml_obj = self.env['account.move.line']

        for k, v in values.items():
            if 'pending' in k:
                pending_obj = self.env['pending.effects.tmp'].browse(
                    int(v))
                if pending_obj:
                    payment_obj = self.env['account.payment.mode'].search([
                        ('name', '=', pending_obj.payment_mode),
                        ('company_id', '=', self.company_id.id)
                    ])
                    values['payment_mode_id'] = payment_obj[0].id
                    values['date_maturity'] = pending_obj.date_maturity
                    if not values['analytic_account_id'] and \
                            pending_obj.analytic_acc:
                        an_obj = self.env['account.analytic.account'].search([
                            ('name', '=', pending_obj.analytic_acc)
                        ])
                        values['analytic_account_id'] = an_obj.id

                pending_obj.used = True
                del values['pending']
                break
        _logger.info("Creating line for %d", i)
        op_ml_obj = op_ml_obj.create(values)

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
        self.op_list = []
        for i in range(len(reader_info)):
            # Don't read rows that start with ( , ' ' or are empty
            if not (reader_info[i][0] is '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                values = dict(zip(keys, field))
                new_values = self._update_values(values)
                self._create_new_opening_journal(new_values, i+2)

        return {'type': 'ir.actions.act_window_close'}
