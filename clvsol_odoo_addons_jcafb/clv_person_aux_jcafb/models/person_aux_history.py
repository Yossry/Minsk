# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

    @api.multi
    def _compute_document_ids_and_count(self):
        for record in self:

            search_domain = [
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ]
            documents_2 = self.env['clv.document'].search(search_domain)

            if record.phase_id.id is not False:
                search_domain.append(
                    ('phase_id.id', '=', record.phase_id.id),
                )
            documents = self.env['clv.document'].search(search_domain)

            record.count_documents = len(documents)
            record.count_documents_2 = len(documents_2)
            record.document_ids = [(6, 0, documents.ids)]

    @api.multi
    def _compute_event_attendee_ids_and_count(self):
        for record in self:

            search_domain = [
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ]
            event_attendees_2 = self.env['clv.event.attendee'].search(search_domain)

            if record.phase_id.id is not False:
                search_domain.append(
                    ('event_phase_id.id', '=', record.phase_id.id),
                )
            event_attendees = self.env['clv.event.attendee'].search(search_domain)

            record.count_events = len(event_attendees)
            record.count_events_2 = len(event_attendees_2)
            record.event_attendee_ids = [(6, 0, event_attendees.ids)]

    @api.multi
    def _compute_lab_test_request_ids_and_count(self):
        for record in self:

            search_domain = [
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ]
            lab_test_requests_2 = self.env['clv.lab_test.request'].search(search_domain)

            if record.phase_id.id is not False:
                search_domain.append(
                    ('phase_id.id', '=', record.phase_id.id),
                )
            lab_test_requests = self.env['clv.lab_test.request'].search(search_domain)

            record.count_lab_test_requests = len(lab_test_requests)
            record.count_lab_test_requests_2 = len(lab_test_requests_2)
            record.lab_test_request_ids = [(6, 0, lab_test_requests.ids)]

    @api.multi
    def _compute_lab_test_result_ids_and_count(self):
        for record in self:

            search_domain = [
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ]
            lab_test_results_2 = self.env['clv.lab_test.result'].search(search_domain)

            if record.phase_id.id is not False:
                search_domain.append(
                    ('phase_id.id', '=', record.phase_id.id),
                )
            lab_test_results = self.env['clv.lab_test.result'].search(search_domain)

            record.count_lab_test_results = len(lab_test_results)
            record.count_lab_test_results_2 = len(lab_test_results_2)
            record.lab_test_result_ids = [(6, 0, lab_test_results.ids)]

    @api.multi
    def _compute_lab_test_report_ids_and_count(self):
        for record in self:

            search_domain = [
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ]
            lab_test_reports_2 = self.env['clv.lab_test.report'].search(search_domain)

            if record.phase_id.id is not False:
                search_domain.append(
                    ('phase_id.id', '=', record.phase_id.id),
                )
            lab_test_reports = self.env['clv.lab_test.report'].search(search_domain)

            record.count_lab_test_reports = len(lab_test_reports)
            record.count_lab_test_reports_2 = len(lab_test_reports_2)
            record.lab_test_report_ids = [(6, 0, lab_test_reports.ids)]
