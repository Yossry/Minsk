# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class PendingEffectsTemp(models.TransientModel):
    _name = 'pending.effects.tmp'

    account = fields.Char(string='Account')
    date_maturity = fields.Date(string='Date maturity')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    payment_mode = fields.Char(string='Payment mode')
    analytic_acc = fields.Char(string='Payment mode')
    used = fields.Boolean(string='Is used', default=False)


class ImportPendingEffects(models.TransientModel):
    _name = 'import.pending.effects'

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

        return values

    '''
        Function to create the opening journal lines.

        :param values: Dict with the values to import.
    '''
    def _create_new_pending_effects(self, values, i):
        _logger.info("Creating pending effect %d", i)
        self.env['pending.effects.tmp'].create(values)

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
            # Don't read rows that start with ( , ' ' or are empty
            if not (reader_info[i][0] is '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                values = dict(zip(keys, field))
                new_values = self._update_values(values)
                self._create_new_pending_effects(new_values, i+2)

        return {'type': 'ir.actions.act_window_close'}
