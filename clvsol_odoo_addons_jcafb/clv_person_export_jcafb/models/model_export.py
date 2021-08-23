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

from odoo import api, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ModelExport(models.Model):
    _inherit = 'clv.model_export'

    @api.model
    def create(self, values):

        ModelExportDocumentItem = self.env['clv.model_export.document_item']
        ModelExportLabTestCriterion = self.env['clv.model_export.lab_test_criterion']

        new_model_export = super().create(values)

        model_export_document_item_ids = []
        for model_export_template_document_item in \
                new_model_export.template_id.model_export_template_document_item_ids:
            values = {
                'name': model_export_template_document_item.name,
                'model_export_id': new_model_export.id,
                'model_export_display': model_export_template_document_item.model_export_display,
                'document_item_id': model_export_template_document_item.document_item_id.id,
                'sequence': model_export_template_document_item.sequence,
            }
            new_model_export_template_document_item = ModelExportDocumentItem.create(values)
            model_export_document_item_ids += [new_model_export_template_document_item.id]

        model_export_lab_test_criterion_ids = []
        for model_export_template_lab_test_criterion in \
                new_model_export.template_id.model_export_template_lab_test_criterion_ids:
            values = {
                'name': model_export_template_lab_test_criterion.name,
                'model_export_id': new_model_export.id,
                'model_export_display': model_export_template_lab_test_criterion.model_export_display,
                'lab_test_criterion_id': model_export_template_lab_test_criterion.lab_test_criterion_id.id,
                'sequence': model_export_template_lab_test_criterion.sequence,
            }
            new_model_export_template_lab_test_criterion = ModelExportLabTestCriterion.create(values)
            model_export_lab_test_criterion_ids += [new_model_export_template_lab_test_criterion.id]

        return new_model_export

    @api.multi
    def write(self, values):

        ModelExportDocumentItem = self.env['clv.model_export.document_item']
        ModelExportLabTestCriterion = self.env['clv.model_export.lab_test_criterion']

        res = super().write(values)

        if 'template_id' in values:

            for model_export_document_item in self.model_export_document_item_ids:
                model_export_document_item.unlink()

            model_export_document_item_ids = []
            for model_export_template_document_item in \
                    self.template_id.model_export_template_document_item_ids:
                values = {
                    'name': model_export_template_document_item.name,
                    'model_export_id': self.id,
                    'model_export_display': model_export_template_document_item.model_export_display,
                    'document_item_id': model_export_template_document_item.document_item_id.id,
                    'sequence': model_export_template_document_item.sequence,
                }
                new_model_export_template_document_item = ModelExportDocumentItem.create(values)
                model_export_document_item_ids += [new_model_export_template_document_item.id]

            for model_export_template_lab_test_criterion in self.model_export_lab_test_criterion_ids:
                model_export_template_lab_test_criterion.unlink()

            model_export_lab_test_criterion_ids = []
            for model_export_template_lab_test_criterion in \
                    self.template_id.model_export_template_lab_test_criterion_ids:
                values = {
                    'name': model_export_template_lab_test_criterion.name,
                    'model_export_id': self.id,
                    'model_export_display': model_export_template_lab_test_criterion.model_export_display,
                    'lab_test_criterion_id': model_export_template_lab_test_criterion.lab_test_criterion_id.id,
                    'sequence': model_export_template_lab_test_criterion.sequence,
                }
                new_model_export_template_lab_test_criterion = ModelExportLabTestCriterion.create(values)
                model_export_lab_test_criterion_ids += [new_model_export_template_lab_test_criterion.id]

        return res


class ModelExport_xls(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_xls_person(self):

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

        if self.use_document_items is not False:

            for document_item in self.model_export_document_item_ids:
                col_name = document_item.document_item_id.code
                if document_item.name is not False:
                    col_name = document_item.name
                row.write(col_nr, col_name)
                col_nr += 1

        if self.use_lab_test_criteria is not False:

            for lab_test_criterion in self.model_export_lab_test_criterion_ids:
                col_name = lab_test_criterion.lab_test_criterion_id.code
                if lab_test_criterion.name is not False:
                    col_name = lab_test_criterion.name
                row.write(col_nr, col_name)
                col_nr += 1

        PersonHistory = self.env['clv.person.history']
        Document = self.env['clv.document']
        LabTestResult = self.env['clv.lab_test.result']
        LabTestReport = self.env['clv.lab_test.report']

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

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

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

                if self.use_document_items is not False:

                    for document_item in self.model_export_document_item_ids:

                        value = None

                        documents = Document.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for document in documents:
                            if document.ref_id.id is not False:
                                if document.document_type_id.id == \
                                   document_item.document_item_id.document_type_id.id:
                                    # value = document.survey_user_input_id.get_value(
                                    #     document_item.document_item_id.code)
                                    value = str(document.get_value(
                                        document_item.document_item_id.code))
                                    break

                        person_histories = PersonHistory.search([
                            ('person_id', '=', eval('item.id')),
                        ])

                        for person_history in person_histories:

                            documents = Document.search([
                                ('ref_id', '=', 'clv.address,' + str(person_history.ref_address_id.id)),
                            ])

                            for document in documents:
                                if document.ref_id.id is not False:
                                    if document.document_type_id.id == \
                                       document_item.document_item_id.document_type_id.id:
                                        # value = document.survey_user_input_id.get_value(
                                        #     document_item.document_item_id.code)
                                        value = str(document.get_value(
                                            document_item.document_item_id.code))
                                        break

                            documents = Document.search([
                                ('ref_id', '=', 'clv.family,' + str(person_history.ref_family_id.id)),
                            ])

                            for document in documents:
                                if document.ref_id.id is not False:
                                    if document.document_type_id.id == \
                                       document_item.document_item_id.document_type_id.id:
                                        # value = document.survey_user_input_id.get_value(
                                        #     document_item.document_item_id.code)
                                        value = str(document.get_value(
                                            document_item.document_item_id.code))
                                        break

                        row.write(col_nr, value)
                        col_nr += 1

                if self.use_lab_test_criteria is not False:

                    for lab_test_criterion in self.model_export_lab_test_criterion_ids:

                        result = None

                        lab_test_results = LabTestResult.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for lab_test_result in lab_test_results:

                            if lab_test_result.lab_test_type_id.id == \
                               lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                result = lab_test_result.criterion_ids.search([
                                    ('lab_test_result_id', '=', lab_test_result.id),
                                    ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                ]).result
                                break

                        if result is None or result is False:

                            lab_test_reports = LabTestReport.search([
                                ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                            ])

                            for lab_test_report in lab_test_reports:

                                if lab_test_report.lab_test_type_id.id == \
                                   lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                    result = lab_test_report.criterion_ids.search([
                                        ('lab_test_report_id', '=', lab_test_report.id),
                                        ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                    ]).result
                                    break

                        if result is None or result is False:

                            person_histories = PersonHistory.search([
                                ('person_id', '=', eval('item.id')),
                            ])

                            for person_history in person_histories:

                                lab_test_results = LabTestResult.search([
                                    ('ref_id', '=', 'clv.address,' + str(person_history.ref_address_id.id)),
                                ])

                            for lab_test_result in lab_test_results:

                                if lab_test_result.lab_test_type_id.id == \
                                   lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                    result = lab_test_result.criterion_ids.search([
                                        ('lab_test_result_id', '=', lab_test_result.id),
                                        ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                    ]).result
                                    break

                            if result is None or result is False:

                                lab_test_reports = LabTestReport.search([
                                    ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                                ])

                                for lab_test_report in lab_test_reports:

                                    if lab_test_report.lab_test_type_id.id == \
                                       lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                        result = lab_test_report.criterion_ids.search([
                                            ('lab_test_report_id', '=', lab_test_report.id),
                                            ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                        ]).result
                                        break

                        row.write(col_nr, result)
                        col_nr += 1

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
    def do_model_export_execute_csv_person(self):

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

        if self.use_document_items is not False:

            for document_item in self.model_export_document_item_ids:
                col_name = document_item.document_item_id.code
                if document_item.name is not False:
                    col_name = document_item.name
                headings.insert(col_nr, col_name)
                col_nr += 1

        if self.use_lab_test_criteria is not False:

            for lab_test_criterion in self.model_export_lab_test_criterion_ids:
                col_name = lab_test_criterion.lab_test_criterion_id.code
                if lab_test_criterion.name is not False:
                    col_name = lab_test_criterion.name
                headings.insert(col_nr, col_name)
                col_nr += 1

        writer.writerow(headings)

        PersonHistory = self.env['clv.person.history']
        Document = self.env['clv.document']
        LabTestResult = self.env['clv.lab_test.result']
        LabTestReport = self.env['clv.lab_test.report']

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

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

                row = []
                col_nr = 0
                if self.export_all_fields is False:
                    for field in self.model_export_field_ids:
                        # row.insert(col_nr, self._get_value_csv(
                        row.insert(col_nr, self._get_value(
                            item, field.field_id,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                else:
                    for field in all_model_fields:
                        # row.insert(col_nr, self._get_value_csv(
                        row.insert(col_nr, self._get_value(
                            item, field,
                            self.export_date_format, self.export_datetime_format)
                        )
                        col_nr += 1

                if self.use_document_items is not False:

                    for document_item in self.model_export_document_item_ids:

                        value = None

                        documents = Document.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for document in documents:
                            if document.ref_id.id is not False:
                                if document.document_type_id.id == \
                                   document_item.document_item_id.document_type_id.id:
                                    # value = document.survey_user_input_id.get_value(
                                    #     document_item.document_item_id.code)
                                    value = str(document.get_value(
                                        document_item.document_item_id.code))
                                    break

                        person_histories = PersonHistory.search([
                            ('person_id', '=', eval('item.id')),
                        ])

                        for person_history in person_histories:

                            documents = Document.search([
                                ('ref_id', '=', 'clv.address,' + str(person_history.ref_address_id.id)),
                            ])

                            for document in documents:
                                if document.ref_id.id is not False:
                                    if document.document_type_id.id == \
                                       document_item.document_item_id.document_type_id.id:
                                        # value = document.survey_user_input_id.get_value(
                                        #     document_item.document_item_id.code)
                                        value = str(document.get_value(
                                            document_item.document_item_id.code))
                                        break

                        row.insert(col_nr, value)
                        col_nr += 1

                if self.use_lab_test_criteria is not False:

                    for lab_test_criterion in self.model_export_lab_test_criterion_ids:

                        result = None

                        lab_test_results = LabTestResult.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for lab_test_result in lab_test_results:

                            if lab_test_result.lab_test_type_id.id == \
                               lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                result = lab_test_result.criterion_ids.search([
                                    ('lab_test_result_id', '=', lab_test_result.id),
                                    ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                ]).result
                                break

                        lab_test_reports = LabTestReport.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for lab_test_report in lab_test_reports:

                            if lab_test_report.lab_test_type_id.id == \
                               lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                result = lab_test_report.criterion_ids.search([
                                    ('lab_test_report_id', '=', lab_test_report.id),
                                    ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                ]).result
                                break

                        row.insert(col_nr, result)
                        col_nr += 1

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
    def do_model_export_execute_sqlite_person(self):

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

        if self.use_document_items is not False:

            for document_item in self.model_export_document_item_ids:
                col_name = document_item.document_item_id.code
                if document_item.name is not False:
                    col_name = document_item.name
                create_table += col_name + ', '
                insert_into_fields += ', ' + col_name
                insert_into_values_1 += ',?'
                col_nr += 1

        if self.use_lab_test_criteria is not False:

            for lab_test_criterion in self.model_export_lab_test_criterion_ids:
                col_name = lab_test_criterion.lab_test_criterion_id.code
                if lab_test_criterion.name is not False:
                    col_name = lab_test_criterion.name
                create_table += col_name + ', '
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

        PersonHistory = self.env['clv.person.history']
        Document = self.env['clv.document']
        LabTestResult = self.env['clv.lab_test.result']
        LabTestReport = self.env['clv.lab_test.report']

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

                _logger.info(u'>>>>>>>>>>>>>>> %s %s', item_count, item)

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

                if self.use_document_items is not False:

                    for document_item in self.model_export_document_item_ids:

                        value = None

                        documents = Document.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for document in documents:
                            if document.ref_id.id is not False:
                                if document.document_type_id.id == \
                                   document_item.document_item_id.document_type_id.id:
                                    # value = document.survey_user_input_id.get_value(
                                    #     document_item.document_item_id.code)
                                    value = str(document.get_value(
                                        document_item.document_item_id.code))
                                    break

                        person_histories = PersonHistory.search([
                            ('person_id', '=', eval('item.id')),
                        ])

                        for person_history in person_histories:

                            documents = Document.search([
                                ('ref_id', '=', 'clv.address,' + str(person_history.ref_address_id.id)),
                            ])

                            for document in documents:
                                if document.ref_id.id is not False:
                                    if document.document_type_id.id == \
                                       document_item.document_item_id.document_type_id.id:
                                        # value = document.survey_user_input_id.get_value(
                                        #     document_item.document_item_id.code)
                                        value = str(document.get_value(
                                            document_item.document_item_id.code))
                                        break

                        values += (value,)
                        col_nr += 1

                if self.use_lab_test_criteria is not False:

                    for lab_test_criterion in self.model_export_lab_test_criterion_ids:

                        result = None

                        lab_test_results = LabTestResult.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for lab_test_result in lab_test_results:

                            if lab_test_result.lab_test_type_id.id == \
                               lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                result = lab_test_result.criterion_ids.search([
                                    ('lab_test_result_id', '=', lab_test_result.id),
                                    ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                ]).result
                                break

                        lab_test_reports = LabTestReport.search([
                            ('ref_id', '=', 'clv.person,' + str(eval('item.id'))),
                        ])

                        for lab_test_report in lab_test_reports:

                            if lab_test_report.lab_test_type_id.id == \
                               lab_test_criterion.lab_test_criterion_id.lab_test_type_id.id:
                                result = lab_test_report.criterion_ids.search([
                                    ('lab_test_report_id', '=', lab_test_report.id),
                                    ('code', '=', lab_test_criterion.lab_test_criterion_id.code),
                                ]).result
                                break

                        values += (result,)
                        col_nr += 1

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
