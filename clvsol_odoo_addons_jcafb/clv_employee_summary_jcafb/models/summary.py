# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime
import pytz
import os
import base64

import xlwt

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.tools import human_size

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        ondelete='restrict',
        readonly='True'
    )
    date_summary = fields.Datetime(
        string='Summary Date',
        related='summary_id.date_summary',
        store=False
    )

    @api.multi
    @api.multi
    def _employee_summary_setup(self, dir_path, file_name):

        SummaryTemplate = self.env['clv.summary.template']
        Summary = self.env['clv.summary']

        model_name = 'hr.employee'

        for employee in self:

            _logger.info(u'%s %s', '>>>>> (employee):', employee.name)

            summary_templates = SummaryTemplate.search([
                ('model', '=', model_name),
            ])

            for summary_template in summary_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (summary_template):', summary_template.name)

                summary = Summary.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', employee.id),
                    ('action', '=', summary_template.action),
                ])

                if summary.id is False:

                    summary_values = {}
                    summary_values['model'] = model_name
                    summary_values['res_id'] = employee.id
                    # summary_values['method'] = summary_template.method
                    summary_values['action'] = summary_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(summary_values):', summary_values)
                    summary = Summary.create(summary_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (summary):', summary)

                employee.summary_id = summary.id

                action_call = 'self.env["clv.summary"].' + \
                    summary.action + \
                    '(summary, employee)'

                _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

                if action_call:

                    summary.state = 'Unknown'
                    summary.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            summary._employee_summary_export_xls(summary, employee, dir_path, file_name)


class Summary(models.Model):
    _inherit = 'clv.summary'

    def _employee_summary(self, summary, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_summary = datetime.now()

        Document = self.env['clv.document']
        SummaryDocument = self.env['clv.summary.document']
        LabTestRequest = self.env['clv.lab_test.request']
        LabTestResult = self.env['clv.lab_test.result']
        LabTestReport = self.env['clv.lab_test.report']
        SummaryLabTestRequest = self.env['clv.summary.lab_test.request']
        SummaryLabTestResult = self.env['clv.summary.lab_test.result']
        SummaryLabTestReport = self.env['clv.summary.lab_test.report']
        Address = self.env['clv.address']
        SummaryAddress = self.env['clv.summary.address']
        Family = self.env['clv.family']
        SummaryFamily = self.env['clv.summary.family']
        Person = self.env['clv.person']
        SummaryPerson = self.env['clv.summary.person']

        summary_documents = SummaryDocument.search([
            ('summary_id', '=', summary.id),
        ])
        summary_documents.unlink()

        summary_lab_test_requests = SummaryLabTestRequest.search([
            ('summary_id', '=', summary.id),
        ])
        summary_lab_test_requests.unlink()

        summary_lab_test_results = SummaryLabTestResult.search([
            ('summary_id', '=', summary.id),
        ])
        summary_lab_test_results.unlink()

        summary_lab_test_reports = SummaryLabTestReport.search([
            ('summary_id', '=', summary.id),
        ])
        summary_lab_test_reports.unlink()

        summary_addresses = SummaryAddress.search([
            ('summary_id', '=', summary.id),
        ])
        summary_addresses.unlink()

        summary_families = SummaryFamily.search([
            ('summary_id', '=', summary.id),
        ])
        summary_families.unlink()

        summary_persons = SummaryPerson.search([
            ('summary_id', '=', summary.id),
        ])
        summary_persons.unlink()

        search_domain = [
            ('employee_id', '=', model_object.id),
        ]
        addresses = Address.search(search_domain)

        search_domain = [
            ('employee_id', '=', model_object.id),
        ]
        families = Family.search(search_domain)

        search_domain = [
            ('employee_id', '=', model_object.id),
        ]
        persons = Person.search(search_domain)

        for address in addresses:

            values = {
                'summary_id': summary.id,
                'address_id': address.id,
            }
            SummaryAddress.create(values)

            search_domain = [
                ('ref_id', '=', 'clv.address' + ',' + str(address.id)),
            ]
            documents = Document.search(search_domain)
            lab_test_requests = LabTestRequest.search(search_domain)
            lab_test_results = LabTestResult.search(search_domain)
            lab_test_reports = LabTestReport.search(search_domain)

            for document in documents:

                if document.phase_id.id == address.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'document_id': document.id,
                    }
                    SummaryDocument.create(values)

            for lab_test_request in lab_test_requests:

                if lab_test_request.phase_id.id == address.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_request_id': lab_test_request.id,
                    }
                    SummaryLabTestRequest.create(values)

            for lab_test_result in lab_test_results:

                if lab_test_result.phase_id.id == address.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_result_id': lab_test_result.id,
                    }
                    SummaryLabTestResult.create(values)

            for lab_test_report in lab_test_reports:

                if lab_test_report.phase_id.id == address.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_report_id': lab_test_report.id,
                    }
                    SummaryLabTestReport.create(values)

        for family in families:

            values = {
                'summary_id': summary.id,
                'family_id': family.id,
            }
            SummaryFamily.create(values)

            search_domain = [
                ('ref_id', '=', 'clv.family' + ',' + str(family.id)),
            ]
            documents = Document.search(search_domain)
            lab_test_requests = LabTestRequest.search(search_domain)
            lab_test_results = LabTestResult.search(search_domain)
            lab_test_reports = LabTestReport.search(search_domain)

            for document in documents:

                if document.phase_id.id == family.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'document_id': document.id,
                    }
                    SummaryDocument.create(values)

            for lab_test_request in lab_test_requests:

                if lab_test_request.phase_id.id == family.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_request_id': lab_test_request.id,
                    }
                    SummaryLabTestRequest.create(values)

            for lab_test_result in lab_test_results:

                if lab_test_result.phase_id.id == family.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_result_id': lab_test_result.id,
                    }
                    SummaryLabTestResult.create(values)

            for lab_test_report in lab_test_reports:

                if lab_test_report.phase_id.id == family.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_report_id': lab_test_report.id,
                    }
                    SummaryLabTestReport.create(values)

        for person in persons:

            values = {
                'summary_id': summary.id,
                'person_id': person.id,
            }
            SummaryPerson.create(values)

            search_domain = [
                ('ref_id', '=', 'clv.person' + ',' + str(person.id)),
            ]
            documents = Document.search(search_domain)
            lab_test_requests = LabTestRequest.search(search_domain)
            lab_test_results = LabTestResult.search(search_domain)
            lab_test_reports = LabTestReport.search(search_domain)

            for document in documents:

                if document.phase_id.id == person.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'document_id': document.id,
                    }
                    SummaryDocument.create(values)

            for lab_test_request in lab_test_requests:

                if lab_test_request.phase_id.id == person.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_request_id': lab_test_request.id,
                    }
                    SummaryLabTestRequest.create(values)

            for lab_test_result in lab_test_results:

                if lab_test_result.phase_id.id == person.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_result_id': lab_test_result.id,
                    }
                    SummaryLabTestResult.create(values)

            for lab_test_report in lab_test_reports:

                if lab_test_report.phase_id.id == person.phase_id.id:

                    values = {
                        'summary_id': summary.id,
                        'lab_test_report_id': lab_test_report.id,
                    }
                    SummaryLabTestReport.create(values)

        summary_values = {}
        summary_values['date_summary'] = date_summary
        summary.write(summary_values)

    def _employee_summary_export_xls(self, summary, model_object, dir_path, file_name):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        model_object_name = model_object._name.replace('.', '_')
        model_object_code = model_object.code

        AddressCategory = self.env['clv.address.category']

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', dir_path),
        ])

        file_name = file_name.replace('<model>', model_object_name).replace('<code>', model_object_code)
        file_path = dir_path + '/' + file_name
        wbook = xlwt.Workbook()
        sheet = wbook.add_sheet(file_name[8:])

        for i in range(0, 49):
            sheet.col(i).width = 256 * 2
        sheet.show_grid = False

        row_nr = 0

        row_nr += 1

        style_bold_str = 'font: bold on'
        style_bold = xlwt.easyxf(style_bold_str)

        style_str = 'font: bold on; font: italic on, height 256'
        style = xlwt.easyxf(style_str)
        sheet.write(row_nr, 0, self.reference_name, style=style)
        sheet.row(row_nr).height = 256
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Summary date:')

        # user_tz = self.env.user.tz
        user_tz = 'America/Argentina/Buenos_Aires'
        local = pytz.timezone(user_tz)
        date_summary_utc = pytz.utc.localize(self.date_summary)
        date_summary_local = date_summary_utc.astimezone(local)
        date_summary_local_str = datetime.strftime(date_summary_local, '%d-%m-%Y %H:%M:%S')

        row.write(9, date_summary_local_str)
        row_nr += 2

        col_address_category = 0
        col_district = 2
        col_address = 4
        col_person = 6

        address_categories = AddressCategory.search([])
        for address_category in address_categories:

            sheet.write(row_nr, col_address_category, address_category.name, style=style_bold)
            row_nr += 2

            districts = []
            for summary_address in summary.summary_address_ids:
                if summary_address.address_category_ids.name == address_category.name:
                    if summary_address.address_id.district not in districts:
                        districts.append(summary_address.address_id.district)

            for district in districts:

                sheet.write(row_nr, col_district, district, style=style_bold)
                row_nr += 2

                addresses = []
                for summary_address in summary.summary_address_ids:
                    if summary_address.address_id.district == district and \
                       summary_address.address_id.state == 'selected':
                        if summary_address.address_id not in addresses:
                            addresses.append(summary_address.address_id)

                for address in addresses:

                    sheet.write(row_nr, col_address, '[' + address.code + ']')
                    sheet.write(row_nr, col_address + 7, address.name, style=style_bold)
                    sheet.write(row_nr, col_address + 36, address.state, style=style_bold)
                    row_nr += 2

                    families = []
                    for summary_family in summary.summary_family_ids:
                        if summary_family.family_id.ref_address_id == address:
                            if summary_family.family_id not in families:
                                families.append(summary_family.family_id)

                    for family in families:

                        sheet.write(row_nr, col_address + 1, '[' + family.code + ']')
                        sheet.write(row_nr, col_address + 1 + 7, family.name, style=style_bold)
                        sheet.write(row_nr, col_address + 1 + 36, family.state, style=style_bold)
                        row_nr += 2

                    persons = []
                    for summary_person in summary.summary_person_ids:
                        if summary_person.person_id.ref_address_id == address and \
                           summary_person.person_id.state == 'selected':
                            if summary_person.person_id not in persons:
                                persons.append(summary_person.person_id)

                    for person in persons:

                        sheet.write(row_nr, col_person, '[' + person.code + ']')
                        sheet.write(row_nr, col_person + 7, person.name, style=style_bold)
                        sheet.write(row_nr, col_person + 30,
                                    '(' + str(person.category_names) + ' - ' + person.age_reference_years + ')')
                        sheet.write(row_nr, col_person + 37, person.state)
                        row_nr += 2

                    persons = []
                    for summary_person in summary.summary_person_ids:
                        if summary_person.person_id.ref_address_id == address and \
                           summary_person.person_id.state == 'waiting':
                            if summary_person.person_id not in persons:
                                persons.append(summary_person.person_id)

                    for person in persons:

                        sheet.write(row_nr, col_person, '[' + person.code + ']')
                        sheet.write(row_nr, col_person + 7, person.name, style=style_bold)
                        sheet.write(row_nr, col_person + 30,
                                    '(' + person.category_names + ' - ' + person.age_reference_years + ')')
                        sheet.write(row_nr, col_person + 37, person.state)
                        row_nr += 2

                addresses = []
                for summary_address in summary.summary_address_ids:
                    if summary_address.address_id.district == district and \
                       summary_address.address_id.state == 'waiting':
                        if summary_address.address_id not in addresses:
                            addresses.append(summary_address.address_id)

                for address in addresses:

                    sheet.write(row_nr, col_address, '[' + address.code + ']')
                    sheet.write(row_nr, col_address + 7, address.name, style=style_bold)
                    sheet.write(row_nr, col_address + 36, address.state, style=style_bold)
                    row_nr += 2

                    families = []
                    for summary_family in summary.summary_family_ids:
                        if summary_family.family_id.ref_address_id == address:
                            if summary_family.family_id not in families:
                                families.append(summary_family.family_id)

                    for family in families:

                        sheet.write(row_nr, col_address + 1, '[' + family.code + ']')
                        sheet.write(row_nr, col_address + 1 + 7, family.name, style=style_bold)
                        sheet.write(row_nr, col_address + 1 + 36, family.state, style=style_bold)
                        row_nr += 2

                    persons = []
                    for summary_person in summary.summary_person_ids:
                        if summary_person.person_id.ref_address_id == address and \
                           summary_person.person_id.state == 'selected':
                            if summary_person.person_id not in persons:
                                persons.append(summary_person.person_id)

                    for person in persons:

                        sheet.write(row_nr, col_person, '[' + person.code + ']')
                        sheet.write(row_nr, col_person + 7, person.name, style=style_bold)
                        sheet.write(row_nr, col_person + 30,
                                    '(' + person.category_names + ' - ' + person.age_reference_years + ')')
                        sheet.write(row_nr, col_person + 37, person.state)
                        row_nr += 2

                    persons = []
                    for summary_person in summary.summary_person_ids:
                        if summary_person.person_id.ref_address_id == address and \
                           summary_person.person_id.state == 'waiting':
                            if summary_person.person_id not in persons:
                                persons.append(summary_person.person_id)

                    for person in persons:

                        sheet.write(row_nr, col_person, '[' + person.code + ']')
                        sheet.write(row_nr, col_person + 7, person.name, style=style_bold)
                        sheet.write(row_nr, col_person + 30,
                                    '(' + person.category_names + ' - ' + person.age_reference_years + ')')
                        sheet.write(row_nr, col_person + 37, person.state)
                        row_nr += 2

        wbook.save(file_path)

        self.directory_id = file_system_directory.id
        self.file_name = file_name
        self.stored_file_name = file_name

        model_object.directory_id = file_system_directory.id
        model_object.file_name = file_name
        model_object.stored_file_name = file_name


class Employee_2(models.Model):
    _inherit = "hr.employee"

    file_name = fields.Char(string='File Name')
    file_content = fields.Binary(
        string='File Content',
        compute='_compute_file'
    )
    stored_file_name = fields.Char(string='Stored File Name')
    directory_id = fields.Many2one(
        comodel_name='clv.file_system.directory',
        string='Directory'
    )

    def _file_read(self, fname, bin_size=False):

        def file_not_found(fname):
            raise Warning(_(
                '''Error while reading file %s.
                Maybe it was removed or permission is changed.
                Please refresh the list.''' % fname))

        self.ensure_one()
        r = ''
        directory = self.directory_id.get_dir() or ''
        full_path = directory + fname
        if not (directory and os.path.isfile(full_path)):
            # file_not_found(fname)
            return False
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                # r = open(full_path, 'rb').read().encode('base64')
                r = base64.b64encode(open(full_path, 'rb').read())
        except (IOError, OSError):
            _logger.info("_read_file reading %s", fname, exc_info=True)
        return r

    @api.depends('stored_file_name')
    def _compute_file(self):
        bin_size = self._context.get('bin_size')
        for file in self:
            if file.stored_file_name:
                content = file._file_read(file.stored_file_name, bin_size)
                file.file_content = content
