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


class Address(models.Model):
    _inherit = 'clv.address'

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
    def _address_summary_setup(self, dir_path, file_name):

        SummaryTemplate = self.env['clv.summary.template']
        Summary = self.env['clv.summary']

        model_name = 'clv.address'

        for address in self:

            _logger.info(u'%s %s', '>>>>> (address):', address.name)

            summary_templates = SummaryTemplate.search([
                ('model', '=', model_name),
            ])

            for summary_template in summary_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (summary_template):', summary_template.name)

                summary = Summary.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', address.id),
                    ('action', '=', summary_template.action),
                ])

                if summary.id is False:

                    summary_values = {}
                    summary_values['model'] = model_name
                    summary_values['res_id'] = address.id
                    # summary_values['method'] = summary_template.method
                    summary_values['action'] = summary_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(summary_values):', summary_values)
                    summary = Summary.create(summary_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (summary):', summary)

                address.summary_id = summary.id

                action_call = 'self.env["clv.summary"].' + \
                    summary.action + \
                    '(summary, address)'

                _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

                if action_call:

                    summary.state = 'Unknown'
                    summary.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            summary._address_summary_export_xls(summary, address, dir_path, file_name)


class Summary(models.Model):
    _inherit = 'clv.summary'

    def _address_summary(self, summary, model_object):

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
        EventAttendee = self.env['clv.event.attendee']
        SummaryEvent = self.env['clv.summary.event']
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

        summary_events = SummaryEvent.search([
            ('summary_id', '=', summary.id),
        ])
        summary_events.unlink()

        summary_families = SummaryFamily.search([
            ('summary_id', '=', summary.id),
        ])
        summary_families.unlink()

        summary_persons = SummaryPerson.search([
            ('summary_id', '=', summary.id),
        ])
        summary_persons.unlink()

        search_domain = [
            ('ref_id', '=', model_object._name + ',' + str(model_object.id)),
        ]
        documents = Document.search(search_domain)
        lab_test_requests = LabTestRequest.search(search_domain)
        lab_test_results = LabTestResult.search(search_domain)
        lab_test_reports = LabTestReport.search(search_domain)
        event_attendees = EventAttendee.search(search_domain)

        search_domain = [
            ('ref_address_id', '=', model_object.id),
        ]
        families = Family.search(search_domain)

        search_domain = [
            ('ref_address_id', '=', model_object.id),
        ]
        persons = Person.search(search_domain)

        for document in documents:

            if document.phase_id.id == model_object.phase_id.id:

                values = {
                    'summary_id': summary.id,
                    'document_id': document.id,
                }
                SummaryDocument.create(values)

        for lab_test_request in lab_test_requests:

            if lab_test_request.phase_id.id == model_object.phase_id.id:

                values = {
                    'summary_id': summary.id,
                    'lab_test_request_id': lab_test_request.id,
                }
                SummaryLabTestRequest.create(values)

        for lab_test_result in lab_test_results:

            if lab_test_result.phase_id.id == model_object.phase_id.id:

                values = {
                    'summary_id': summary.id,
                    'lab_test_result_id': lab_test_result.id,
                }
                SummaryLabTestResult.create(values)

        for lab_test_report in lab_test_reports:

            if lab_test_report.phase_id.id == model_object.phase_id.id:

                values = {
                    'summary_id': summary.id,
                    'lab_test_report_id': lab_test_report.id,
                }
                SummaryLabTestReport.create(values)

        for event_attendee in event_attendees:

            if event_attendee.event_id.phase_id.id == model_object.phase_id.id:

                values = {
                    'summary_id': summary.id,
                    'event_id': event_attendee.event_id.id,
                }
                SummaryEvent.create(values)

        for family in families:

            if family.state not in ['unavailable']:

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

                # for document in documents:

                #     if document.phase_id.id == family.phase_id.id:

                #         values = {
                #             'summary_id': summary.id,
                #             'document_id': document.id,
                #         }
                #         SummaryDocument.create(values)

                # for lab_test_request in lab_test_requests:

                #     if lab_test_request.phase_id.id == family.phase_id.id:

                #         values = {
                #             'summary_id': summary.id,
                #             'lab_test_request_id': lab_test_request.id,
                #         }
                #         SummaryLabTestRequest.create(values)

        for person in persons:

            if person.state not in ['unavailable']:

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

                # for document in documents:

                #     if document.phase_id.id == person.phase_id.id:

                #         values = {
                #             'summary_id': summary.id,
                #             'document_id': document.id,
                #         }
                #         SummaryDocument.create(values)

                # for lab_test_request in lab_test_requests:

                #     if lab_test_request.phase_id.id == person.phase_id.id:

                #         values = {
                #             'summary_id': summary.id,
                #             'lab_test_request_id': lab_test_request.id,
                #         }
                #         SummaryLabTestRequest.create(values)

        summary_values = {}
        summary_values['date_summary'] = date_summary
        summary.write(summary_values)

    def _address_summary_export_xls(self, summary, model_object, dir_path, file_name):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        model_object_name = model_object._name.replace('.', '_')
        model_object_code = model_object.code

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('directory', '=', dir_path),
        ])

        file_name = file_name.replace('<model>', model_object_name).replace('<code>', model_object_code)
        file_path = dir_path + '/' + file_name
        wbook = xlwt.Workbook()
        sheet = wbook.add_sheet(file_name[8:])

        for i in range(12):
            sheet.col(i).width = 256 * 7
        sheet.show_grid = False

        row_nr = 0

        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Summary for:')
        row.write(3, self.reference_name)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Summary date:')

        # user_tz = self.env.user.tz
        user_tz = 'America/Argentina/Buenos_Aires'
        local = pytz.timezone(user_tz)
        date_summary_utc = pytz.utc.localize(self.date_summary)
        date_summary_local = date_summary_utc.astimezone(local)
        date_summary_local_str = datetime.strftime(date_summary_local, '%d-%m-%Y %H:%M:%S')

        row.write(3, date_summary_local_str)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Responsible Employee:')
        row.write(3, model_object.employee_id.name)
        row_nr += 1

        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Address:')
        row.write(3, model_object.name)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(3, model_object.district)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Address Categories:')
        row.write(3, model_object.category_ids.name)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Address Code:')
        row.write(3, model_object.code)
        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Address State:')
        row.write(3, model_object.state)
        row_nr += 1

        # row_nr += 1
        # row = sheet.row(row_nr)
        # row.write(0, 'Document ')
        # row.write(2, 'Code')
        # row.write(4, 'Categories')
        # row_nr += 1
        # sheet.row(row_nr).height_mismatch = True
        # sheet.row(row_nr).height = 20 * 4
        # row_nr += 1

        # for address_document in self.summary_address_document_ids:

        #     row = sheet.row(row_nr)
        #     row.write(0, address_document.document_id.name)
        #     row.write(2, address_document.document_id.code)
        #     row.write(4, address_document.document_category_ids.name)
        #     row_nr += 1

        for summary_family in self.summary_family_ids:

            row_nr += 1
            row = sheet.row(row_nr)
            row.write(0, 'Family:')
            row.write(3, summary_family.family_id.name)
            row_nr += 1
            row = sheet.row(row_nr)
            row.write(0, 'Family Code:')
            row.write(3, summary_family.family_id.code)
            row_nr += 1
            row = sheet.row(row_nr)
            row.write(0, 'Family State:')
            row.write(3, summary_family.family_id.state)
            row_nr += 1

        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Person ')
        row.write(5, 'Code')
        row.write(7, 'Birthday')
        # row.write(8, 'Reference Age')
        # row.write(10, 'Categories')
        # row.write(12, 'Status')
        row.write(9, 'Categories')
        row.write(11, 'Status')
        row_nr += 1
        sheet.row(row_nr).height_mismatch = True
        sheet.row(row_nr).height = 20 * 4
        row_nr += 1

        for summary_person in self.summary_person_ids:

            row = sheet.row(row_nr)
            row.write(0, summary_person.person_id.name)
            row.write(5, summary_person.person_id.code)

            if summary_person.person_id.birthday is not False:
                row.write(7, datetime.strftime(summary_person.person_id.birthday, '%d-%m-%Y'))
            # if summary_person.person_id.age_reference is not False:
            #     row.write(8, summary_person.person_id.age_reference)
            # if summary_person.person_category_ids.name is not False:
            #     row.write(10, summary_person.person_category_ids.name)
            # row.write(12, summary_person.person_state)
            if summary_person.person_category_ids.name is not False:
                row.write(9, summary_person.person_category_ids.name)
            row.write(11, summary_person.person_state)
            row_nr += 1

        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Document ')
        row.write(2, 'Code')
        row.write(4, 'Categories')
        row_nr += 1
        sheet.row(row_nr).height_mismatch = True
        sheet.row(row_nr).height = 20 * 4
        row_nr += 1

        for summary_document in self.summary_document_ids:

            row = sheet.row(row_nr)
            row.write(0, summary_document.document_id.name)
            row.write(2, summary_document.document_id.code)
            row.write(4, summary_document.document_category_ids.name)
            row_nr += 1

        row_nr += 1
        row = sheet.row(row_nr)
        row.write(0, 'Lab Test Type ')
        row.write(8, 'Lab Test Request')
        row_nr += 1
        sheet.row(row_nr).height_mismatch = True
        sheet.row(row_nr).height = 20 * 4
        row_nr += 1

        for summary_lab_test_request in self.summary_lab_test_request_ids:

            row = sheet.row(row_nr)
            row.write(0, summary_lab_test_request.lab_test_type_ids.name)
            row.write(8, summary_lab_test_request.lab_test_request_id.code)
            row_nr += 1

        wbook.save(file_path)

        self.directory_id = file_system_directory.id
        self.file_name = file_name
        self.stored_file_name = file_name

        model_object.directory_id = file_system_directory.id
        model_object.file_name = file_name
        model_object.stored_file_name = file_name


class Address_2(models.Model):
    _inherit = "clv.address"

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
