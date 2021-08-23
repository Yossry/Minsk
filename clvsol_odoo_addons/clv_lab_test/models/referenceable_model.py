# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class LabTestRequest(models.Model):
    _name = "clv.lab_test.request"
    _inherit = 'clv.lab_test.request', 'clv.abstract.reference'


class LabTestResult(models.Model):
    _name = "clv.lab_test.result"
    _inherit = 'clv.lab_test.result', 'clv.abstract.reference'


class LabTestReport(models.Model):
    _name = "clv.lab_test.report"
    _inherit = 'clv.lab_test.report', 'clv.abstract.reference'
