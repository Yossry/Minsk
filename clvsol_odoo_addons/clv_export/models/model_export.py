# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import *
from time import time
import xlwt
import csv
import sqlite3
from functools import reduce

from odoo import api, fields, models
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import exceptions

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractModelExport(models.AbstractModel):
    _inherit = 'clv.abstract.model_export'

    def model_export_file_name(self, export_type):
        if export_type == 'xls':
            return '<model>_<label>_<code>_<timestamp>.xls'
        if export_type == 'csv':
            return '<model>_<label>_<code>_<timestamp>.csv'
        if export_type == 'sqlite':
            return '<dbname>_<label>.sqlite'
        return False


class ModelExport(models.Model):
    _description = 'Model Export'
    _name = 'clv.model_export'
    _inherit = 'clv.abstract.model_export'

    code = fields.Char(string='Model Export Code', required=False)

    template_id = fields.Many2one(
        comodel_name='clv.model_export.template',
        string='Model Export Template',
        required=False,
        ondelete='restrict'
    )

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]

    @api.onchange('template_id')
    def onchange_template_id(self):

        if self.template_id:
            self.name = self.template_id.name
            self.label = self.template_id.label
            self.model_id = self.template_id.model_id
            self.export_type = self.template_id.export_type
            self.notes = self.template_id.notes

    @api.onchange('export_type')
    def onchange_export_type(self):

        if self.export_type:
            self.export_dir_path = self.model_export_dir_path(self.export_type)
            self.export_file_name = self.model_export_file_name(self.export_type)

    export_set_id = fields.Many2one(
        comodel_name='clv.set',
        string='Set',
        ondelete='restrict'
    )
    count_export_set_elements = fields.Integer(
        string='Set Elements (count)',
        compute='_compute_count_export_set_elements',
        store=False
    )

    @api.depends('export_set_id')
    def _compute_count_export_set_elements(self):
        for r in self:
            r.count_export_set_elements = len(r.export_set_id.set_element_ids)

    @api.model
    def create(self, values):

        ModelExportField = self.env['clv.model_export.field']

        new_model_export = super().create(values)

        model_export_field_ids = []
        for model_export_template_field in new_model_export.template_id.model_export_template_field_ids:
            values = {
                'name': model_export_template_field.name,
                'model_export_id': new_model_export.id,
                'model_export_display': model_export_template_field.model_export_display,
                'field_id': model_export_template_field.field_id.id,
                'sequence': model_export_template_field.sequence,
            }
            new_model_export_template_field = ModelExportField.create(values)
            model_export_field_ids += [new_model_export_template_field.id]

        return new_model_export

    @api.multi
    def write(self, values):

        ModelExportField = self.env['clv.model_export.field']

        res = super().write(values)

        if 'template_id' in values:

            for model_export_field in self.model_export_field_ids:
                model_export_field.unlink()

            model_export_field_ids = []
            for model_export_template_field in self.template_id.model_export_template_field_ids:
                values = {
                    'name': model_export_template_field.name,
                    'model_export_id': self.id,
                    'model_export_display': model_export_template_field.model_export_display,
                    'field_id': model_export_template_field.field_id.id,
                    'sequence': model_export_template_field.sequence,
                }
                new_model_export_template_field = ModelExportField.create(values)
                model_export_field_ids += [new_model_export_template_field.id]

        return res

    @api.multi
    def copy(self):
        raise exceptions.ValidationError('It is not possible to duplicate the record, please create a new one.')


class ModelExportTemplate(models.Model):
    _inherit = 'clv.model_export.template'

    model_export_ids = fields.One2many(
        comodel_name='clv.model_export',
        inverse_name='template_id',
        string='Model Exports'
    )
    count_model_exports = fields.Integer(
        string='Model Exports (count)',
        compute='_compute_count_model_exports',
        store=True
    )

    @api.multi
    @api.depends('model_export_ids')
    def _compute_count_model_exports(self):
        for r in self:
            r.count_model_exports = len(r.model_export_ids)


class ModelExport_get_value(models.Model):
    _inherit = 'clv.model_export'

    @api.model
    def _get_value(self, item, field, export_date_format, export_datetime_format):

        if field.ttype == 'date':
            cmd = 'item.' + field.name
            if eval(cmd) is not False:
                # date_value = eval(cmd)
                date_value = str(eval(cmd))
                # date_obj = datetime.strptime(date_value, DEFAULT_SERVER_DATE_FORMAT)
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                try:
                    date_formated = datetime.strftime(date_obj, export_date_format)
                except Exception:
                    date_formated = date_value
                cmd = '"' + date_formated + '"'
            else:
                cmd = 'False'
        elif field.ttype == 'datetime':
            cmd = 'item.' + field.name
            if eval(cmd) is not False:
                # datetime_value = eval(cmd)
                datetime_value = str(eval(cmd))
                # datetime_obj = datetime.strptime(datetime_value, DEFAULT_SERVER_DATETIME_FORMAT)
                try:
                    datetime_obj = datetime.strptime(datetime_value, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    datetime_obj = datetime.strptime(datetime_value, "%Y-%m-%d %H:%M:%S")
                try:
                    datetime_formated = datetime.strftime(datetime_obj, export_datetime_format)
                except Exception:
                    datetime_formated = datetime_value
                cmd = '"' + datetime_formated + '"'
            else:
                cmd = 'False'
        elif field.ttype == 'many2many':
            cmd = 'item.' + field.name
            ids = eval(cmd)
            names_str = '"'
            for id_ in ids:
                if names_str == '"':
                    names_str += id_.name
                else:
                    names_str += '; ' + id_.name
            names_str += '"'
            cmd = names_str
            # cmd = names_str.encode('ascii', 'replace')
            # cmd = names_str.encode('ascii', 'xmlcharrefreplace')
        elif field.ttype == 'many2one':
            cmd = 'item.' + field.name + '.name'
        elif field.ttype == 'one2many':
            cmd = 'item.' + field.name
            cmd = str(len(eval(cmd)))
        elif field.ttype == 'binary':
            cmd = 'False'
        else:
            cmd = 'item.' + field.name

        eval_cmd = False
        try:
            eval_cmd = eval(cmd)
        except Exception as e:
            _logger.warning(u'%s %s [%s]', '>>>>>>>>>> Exception: ', e, field.name)
        if cmd != 'False' and eval_cmd is not False:
            return eval(cmd)
        else:
            return None


class ModelExport_xls(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_xls(self):

        start = time()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', self.export_dir_path),
        ])

        IRModelFields = self.env['ir.model.fields']
        all_model_fields = IRModelFields.search([
            ('model_id', '=', self.model_id.id),
        ])

        self.date_export = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        model_name = self.model_id.model.replace('.', '_')
        # label = ''
        # if self.label is not False:
        #     label = '_' + self.label
        label = self.label
        code = self.code
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[2:]
        file_name = self.export_file_name\
            .replace('<model>', model_name)\
            .replace('<label>', label)\
            .replace('<code>', code)\
            .replace('<timestamp>', timestamp)
        file_path = self.export_dir_path + '/' + file_name
        _logger.info(u'%s %s', '>>>>>>>>>>', file_path)

        book = xlwt.Workbook()

        sheet = book.add_sheet(file_name)
        row_nr = 0

        row = sheet.row(row_nr)
        col_nr = 0
        if self.export_all_fields is False:
            for field in self.model_export_field_ids:
                col_name = field.field_id.field_description
                if field.name is not False:
                    col_name = field.name
                row.write(col_nr, col_name)
                col_nr += 1
        else:
            for field in all_model_fields:
                col_name = field.name
                row.write(col_nr, col_name)
                col_nr += 1

        item_count = 0
        items = False
        if (self.export_all_items is False) and \
           (self.export_set_elements is False) and \
           (self.model_items is not False):
            items = eval('self.' + self.model_items)
        elif (self.export_all_items is False) and \
             (self.export_set_elements is True) and \
             (self.export_set_id is not False):
            set_elements = self.export_set_id.set_element_ids
            items = []
            for set_element in set_elements:
                items.append(set_element.ref_id)
        elif self.export_all_items is True:
            Model = self.env[self.model_model]
            items = Model.search(eval(self.export_domain_filter))

        if items is not False:
            for item in items:
                item_count += 1
                row_nr += 1
                row = sheet.row(row_nr)
                col_nr = 0
                if self.export_all_fields is False:
                    for field in self.model_export_field_ids:
                        row.write(col_nr, self._get_value(
                            item, field.field_id,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                else:
                    for field in all_model_fields:
                        row.write(col_nr, self._get_value(
                            item, field,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

        book.save(file_path)

        self.directory_id = file_system_directory.id
        self.file_name = file_name
        self.stored_file_name = file_name

        _logger.info(u'%s %s', '>>>>>>>>>> file_path: ', file_path)
        _logger.info(u'%s %s', '>>>>>>>>>> item_count: ', item_count)
        _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))


class ModelExport_csv(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_csv(self):

        start = time()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', self.export_dir_path),
        ])

        IRModelFields = self.env['ir.model.fields']
        all_model_fields = IRModelFields.search([
            ('model_id', '=', self.model_id.id),
        ])

        self.date_export = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        model_name = self.model_id.model.replace('.', '_')
        label = ''
        if self.label is not False:
            label = '_' + self.label
        code = self.code
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[2:]
        file_name = self.export_file_name\
            .replace('<model>', model_name)\
            .replace('_<label>', label)\
            .replace('<code>', code)\
            .replace('<timestamp>', timestamp)
        file_path = self.export_dir_path + '/' + file_name
        _logger.info(u'%s %s', '>>>>>>>>>>', file_path)

        file = open(file_path, 'w', newline='')
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

        headings = []

        col_nr = 0
        if self.export_all_fields is False:
            for field in self.model_export_field_ids:
                col_name = field.field_id.field_description
                if field.name is not False:
                    col_name = field.name
                headings.insert(col_nr, col_name)
                col_nr += 1
        else:
            for field in all_model_fields:
                col_name = field.name
                headings.insert(col_nr, col_name)
                col_nr += 1

        writer.writerow(headings)

        item_count = 0
        items = False
        if (self.export_all_items is False) and \
           (self.export_set_elements is False) and \
           (self.model_items is not False):
            items = eval('self.' + self.model_items)
        elif (self.export_all_items is False) and \
             (self.export_set_elements is True) and \
             (self.export_set_id is not False):
            set_elements = self.export_set_id.set_element_ids
            items = []
            for set_element in set_elements:
                items.append(set_element.ref_id)
        elif self.export_all_items is True:
            Model = self.env[self.model_model]
            items = Model.search(eval(self.export_domain_filter))

        if items is not False:
            for item in items:
                item_count += 1
                row = []
                col_nr = 0
                if self.export_all_fields is False:
                    for field in self.model_export_field_ids:
                        row.insert(col_nr, self._get_value(
                            item, field.field_id,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                else:
                    for field in all_model_fields:
                        row.insert(col_nr, self._get_value(
                            item, field,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

                writer.writerow(row)

        file.close()

        self.directory_id = file_system_directory.id
        self.file_name = file_name
        self.stored_file_name = file_name

        _logger.info(u'%s %s', '>>>>>>>>>> file_path: ', file_path)
        _logger.info(u'%s %s', '>>>>>>>>>> item_count: ', item_count)
        _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))


class ModelExport_sqlite(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_sqlite(self):

        start = time()

        db_name = self._cr.dbname
        table_name = self.model_model.replace('.', '_')
        label = ''
        if self.label is not False:
            label = '_' + self.label
        file_name = self.export_file_name\
            .replace('<dbname>', db_name)\
            .replace('_<label>', label)
        db_path = self.export_dir_path + '/' + file_name
        _logger.info(u'%s %s', '>>>>>>>>>>', db_path)

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', self.export_dir_path),
        ])

        IRModelFields = self.env['ir.model.fields']
        all_model_fields = IRModelFields.search([
            ('model_id', '=', self.model_id.id),
        ])

        conn = sqlite3.connect(db_path)
        conn.text_factory = str

        cursor = conn.cursor()
        try:
            cursor.execute('''DROP TABLE ''' + table_name + ''';''')
        except Exception as e:
            print('------->', e)

        create_table = 'CREATE TABLE ' + table_name + ' ('

        insert_into = 'INSERT INTO ' + table_name
        insert_into_fields = ''
        insert_into_values_1 = ''

        col_nr = 0
        if self.export_all_fields is False:
            for field in self.model_export_field_ids:

                col_name = field.field_id.name
                if col_name == 'values':
                    col_name = "'" + col_name + "'"

                if col_name == 'id':
                    create_table += 'id INTEGER NOT NULL PRIMARY KEY, '
                else:
                    if field.name is not False:
                        col_name = field.name
                    create_table += col_name + ', '
                if col_nr == 0:
                    insert_into_fields += col_name
                    insert_into_values_1 += '?'
                else:
                    insert_into_fields += ', ' + col_name
                    insert_into_values_1 += ',?'
                col_nr += 1
        else:
            for field in all_model_fields:

                col_name = field.name
                if col_name == 'values':
                    col_name = "'" + col_name + "'"

                if col_name == 'id':
                    create_table += 'id INTEGER NOT NULL PRIMARY KEY, '
                else:
                    create_table += col_name + ', '
                if col_nr == 0:
                    insert_into_fields += col_name
                    insert_into_values_1 += '?'
                else:
                    insert_into_fields += ', ' + col_name
                    insert_into_values_1 += ',?'
                col_nr += 1

        create_table += 'new_id INTEGER'
        create_table += ');'

        _logger.info(u'%s %s', '>>>>>>>>>> create_table:', create_table)

        insert_into += ' (' + insert_into_fields + \
                       ') VALUES(' + insert_into_values_1 + ')'

        _logger.info(u'%s %s', '>>>>>>>>>> insert_into:', insert_into)

        cursor.execute(create_table)

        self.date_export = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        item_count = 0
        items = False
        if (self.export_all_items is False) and \
           (self.export_set_elements is False) and \
           (self.model_items is not False):
            items = eval('self.' + self.model_items)
        elif (self.export_all_items is False) and \
             (self.export_set_elements is True) and \
             (self.export_set_id is not False):
            set_elements = self.export_set_id.set_element_ids
            items = []
            for set_element in set_elements:
                items.append(set_element.ref_id)
        elif self.export_all_items is True:
            Model = self.env[self.model_model]
            items = Model.search(eval(self.export_domain_filter))

        row_nr = 0
        if items is not False:
            for item in items:
                item_count += 1
                row_nr += 1
                col_nr = 0
                values = ()
                if self.export_all_fields is False:
                    for field in self.model_export_field_ids:
                        values += (self._get_value(
                            item, field.field_id,
                            self.export_date_format, self.export_datetime_format),
                        )
                        col_nr += 1

                else:
                    for field in all_model_fields:
                        values += (self._get_value(
                            item, field,
                            self.export_date_format, self.export_datetime_format),
                        )
                        col_nr += 1

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

                cursor.execute(insert_into, values)

        conn.commit()
        conn.close()

        self.directory_id = file_system_directory.id
        self.file_name = file_name
        # self.stored_file_name = file_name
        self.stored_file_name = False

        _logger.info(u'%s %s', '>>>>>>>>>> db_path: ', db_path)
        _logger.info(u'%s %s', '>>>>>>>>>> item_count: ', item_count)
        _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))
