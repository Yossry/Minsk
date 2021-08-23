# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def create_employee_from_applicant(self):
        employee_action_window = super().create_employee_from_applicant()
        # note: this function does not use `ensure_one`. It returns the
        # action window on the last created employee.

        for applicant in self:
            employee = applicant.emp_id
            for document in applicant.attachment_ids:
                employee_document = document.copy()
                employee_document.res_model = employee._name
                employee_document.res_id = employee.id

        return employee_action_window
