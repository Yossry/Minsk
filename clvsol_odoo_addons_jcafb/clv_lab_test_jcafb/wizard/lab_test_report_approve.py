# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestReportApprove(models.TransientModel):
    _description = 'Lab Test Report Approve'
    _name = 'clv.lab_test.report.approve'

    def _default_lab_test_report_ids(self):
        return self._context.get('active_ids')
    lab_test_report_ids = fields.Many2many(
        comodel_name='clv.lab_test.report',
        relation='clv_lab_test_report_lab_test_report_approve_rel',
        string='Lab Test Reports',
        readonly=True,
        default=_default_lab_test_report_ids
    )

    approved = fields.Boolean(string='Approved', default=True)

    def _default_employee_id(self):
        HrEmployee = self.env['hr.employee']
        employee = HrEmployee.search([
            ('user_id', '=', self.env.uid),
        ])
        if employee.id is not False:
            return employee.id
        return False
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approved by',
        # required=True,
        default=_default_employee_id
    )

    date_approved = fields.Date(
        string='Approved Date',
        # required=True,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d'),
    )

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_lab_test_report_approve(self):
        self.ensure_one()

        for lab_test_report in self.lab_test_report_ids:

            _logger.info(u'%s %s %s', '>>>>>', lab_test_report.code, lab_test_report.ref_id.name)

            # if lab_test_report.state == 'available':

            _logger.info(u'%s %s %s', '>>>>>', self.employee_id.name, self.date_approved)

            if self.approved:

                lab_test_report.approved = self.approved
                lab_test_report.employee_id = self.employee_id
                lab_test_report.date_approved = self.date_approved
                lab_test_report.state = 'approved'

            else:

                lab_test_report.approved = False
                lab_test_report.employee_id = False
                lab_test_report.date_approved = False
                lab_test_report.state = 'available'

        return True
