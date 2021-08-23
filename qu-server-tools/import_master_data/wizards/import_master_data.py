# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _

import base64
import csv
from io import StringIO

from lxml import etree
from lxml import builder


class ImportMasterData(models.TransientModel):
    _name = 'import.master.data'

    data = fields.Binary(string='File', required=True)
    name = fields.Char(string='Filename')
    delimeter = fields.Char(
        string='Delimiter',
        default=',',
        help='Default delimiter ","',
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
    )
    key_field_id = fields.Many2one(
        'ir.model.fields',
        string='Key field',
        help='Field used to generate XML ID',
    )
    xml_file = fields.Binary(string='XML File')

    '''
        Convert csv rows into a xml file.

        :param str root: root of the xml
        :param str values: csv row values
        :param int counter: counter for each row
    '''
    def csv_row_to_xml(self, root, values, counter):
        model = self.model_id.model
        record_id = model.replace(".", "_") + '_data'
        if self.key_field_id:
            record_id = record_id + values[self.key_field_id.name]
        else:
            record_id = record_id + str(counter)

        record = etree.SubElement(root, "record", id=record_id, model=model)

        for field in values.keys():
            record_field = etree.SubElement(
                record, "field", name=field).text = values[field]

    '''
        Function to read the csv file and convert it to a dict.
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

        counter = 1

        # Start XML Tree
        root = etree.Element("odoo")

        for i in range(len(reader_info)):
            # Don't read rows that start with ( , ' ' or are empty
            if not (reader_info[i][0] is '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                values = dict(zip(keys, field))

                # Build XML Tree with the CSV rows
                self.csv_row_to_xml(root, values, counter)
                counter += 1

        # Save the XML file
        filename = '%s_data.xml' % (self.model_id.model.replace(".", "_"))
        xml_string = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        self.write({
            'xml_file': base64.b64encode(xml_string),
        })

        # Call the controller to download the XML file
        return {
             'type': 'ir.actions.act_url',
             'url': '/web/binary/download_data?filename=%s&model_id=%s' % (
                filename, self.id),
             'target': 'self',
        }
