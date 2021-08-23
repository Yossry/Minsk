# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportProduct(models.TransientModel):
    _name = 'import.product'

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
        for k, v in values.items():
            if v == 'True':
                values[k] = True
            elif v == 'False':
                values[k] = False

        if values['standard_price']:
            values['standard_price'] = values[
                'standard_price'].replace('.', '')
            values['standard_price'] = values[
                'standard_price'].replace(',', '.')

        if values['list_price']:
            values['list_price'] = values['list_price'].replace('.', '')
            values['list_price'] = values['list_price'].replace(',', '.')

        if values['supplier_price']:
            values['supplier_price'] = values[
                'supplier_price'].replace('.', '')
            values['supplier_price'] = values[
                'supplier_price'].replace(',', '.')

        return values

    '''
        Function to assign not direct mapping data.

        :param values: Dict with the values to import.

        :return Dict with the correct mapping.
    '''
    def _assign_product_data(self, values):
        product_data = {}
        # Assign or create a category
        if values['categ_id']:
            categ_obj = self.env['product.category'].search([(
                'name', '=', values['categ_id'])])

            if not categ_obj:
                categ_values = {}
                categ_values = {
                    'name': values['categ_id'],
                    'parent_id': 2,
                }
                categ_obj = categ_obj.create(categ_values)
            product_data.update({
                    'categ_id': categ_obj.id,
            })
        else:
            product_data.update({
                    'categ_id': 2,
            })
        del values['categ_id']

        # Assign or update uom
        if values['uom']:
            uom_obj = self.env.ref(values['uom'])
            if uom_obj:
                product_data.update({
                    'uom_id': uom_obj.id,
                    'uom_po_id': uom_obj.id,
                })
        del values['uom']

        # Assign or update a supplier

        if values['supplier_code']:
            supplier_obj = self.env[
                'res.partner'].search([
                    ('unique_code', '=', values['supplier_code']),
                    ('supplier', '=', True)
                ])
            if supplier_obj:
                new_supplier = True
                product_obj = self.env[
                    'product.template'].search([(
                        'default_code', '=', values['default_code'])
                    ])
                currency_obj = self.env[
                    'res.currency'].search([(
                        'name', '=', values['supplier_currency'])])
                product_sellers = product_obj.seller_ids
                if product_sellers:
                    for seller in product_sellers:
                        if seller.name.unique_code == values['supplier_code']:
                            seller_values = {}
                            seller_values = {
                                'min_qty': values['supplier_min_qty'],
                                'price': values['supplier_price'],
                            }
                            if currency_obj:
                                seller_values.update({
                                    'currency_id': currency_obj.id,
                                })
                            product_data.update({
                                    'seller_ids': [(1, seller.id, seller_values)],
                            })
                            new_supplier = False
                            break
                if new_supplier:
                    seller_values = {}
                    seller_values = {
                        'name': supplier_obj.id,
                        'min_qty': values['supplier_min_qty'],
                        'price': values['supplier_price'],
                    }
                    if currency_obj:
                        seller_values.update({
                            'currency_id': currency_obj.id,
                        })
                    product_data.update({
                        'seller_ids': [(0, 0, seller_values)],
                    })

        del values['supplier_code']
        del values['supplier_min_qty']
        del values['supplier_price']
        del values['supplier_currency']

        return product_data

    '''
        Function to create or write the product.

        :param values: Dict with the values to import.
    '''
    def _create_new_product(self, values):
        # Update existing customers
        current_product = self.env['product.template'].search([
            ('name', '=', values['name'])])
        fields = {}
        fields = self._assign_product_data(values)
        if current_product:
            current_product.write(values)
            _logger.info("Updating product: %s", current_product.name)
        else:
            current_product = current_product.create(values)
            _logger.info("Creating product: %s", current_product.name)

        current_product.write(fields)

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
                self._create_new_product(new_values)

        return {'type': 'ir.actions.act_window_close'}
