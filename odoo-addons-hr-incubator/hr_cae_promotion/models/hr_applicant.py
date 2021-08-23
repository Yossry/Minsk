# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Applicant(models.Model):
    _inherit = "hr.applicant"

    promotion_id = fields.Many2one(
        comodel_name="hr.promotion", string="Promotion", required=False
    )

    @api.multi
    def create_employee_from_applicant(self):
        employee_action_window = super().create_employee_from_applicant()
        # note: this function does not use `ensure_one`. It returns the
        # action window on the last created employee.

        for applicant in self:
            employee = applicant.emp_id
            employee.promotion_id = applicant.promotion_id

        return employee_action_window
