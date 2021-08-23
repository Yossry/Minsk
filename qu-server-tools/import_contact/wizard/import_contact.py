# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportContact(models.TransientModel):
    _name = 'import.contact'

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimiter', default=',',
                            help='Default delimiter ","')

    '''
        Function to update and correct some values.

        :param values: Dict with the values to import.

        :return Dict with the modified values modifieds.
    '''
    def _update_values(self, values):

        if values['parent_id']:
            parent_obj = self.env['res.partner'].search([(
                'unique_code', '=', values['parent_id'])])
            if parent_obj:
                values['parent_id'] = parent_obj.id
            else:
                values['parent_id'] = False

        return values

    '''
        Function to assign not direct mapping data.

        :param values: Dict with the values to import.

        :return Dict with the correct mapping.
    '''

    def _assign_contact_data(self, values):
        contact_data = {}

        if values['language']:
            language_obj = self.env[
                'res.lang'].search([
                    ('iso_code', '=', values['language'])])
            if language_obj:
                contact_data.update({
                    'lang': language_obj.code,
                })

        del values['language']

        return contact_data

    '''
        Function to create or write the partner / supplier.

        :param values: Dict with the values to import.
    '''
    def _create_new_contact(self, values):
        # Update existing customers
        contact = self.env['res.partner'].search([
            ('unique_code', '=', values['unique_code'])])
        if values['parent_id']:
            fields = {}
            fields = self._assign_contact_data(values)
            if contact:
                contact.write(values)
                _logger.info("Updating contact: %s", contact.unique_code)
            else:
                contact = contact.create(values)
                _logger.info("Creating contact: %s", contact.unique_code)

            contact.write(fields)
        else:
            _logger.info("Parent Partner not Found")

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
                new_values = self._update_values(values)
                self._create_new_contact(new_values)

        return {'type': 'ir.actions.act_window_close'}
