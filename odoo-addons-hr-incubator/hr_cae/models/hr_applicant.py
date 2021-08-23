# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Applicant(models.Model):
    _inherit = "hr.applicant"

    currency_id = fields.Many2one(
        string="Currency", related="company_id.currency_id", readonly=True
    )
    title = fields.Many2one("res.partner.title")
    job = fields.Char(string="Job", required=False)
    job_description = fields.Text(string="Job Description", required=False)
    equipment = fields.Text(string="Equipment", required=False)
    type_id = fields.Many2one("hr.recruitment.degree", string="Certificate")
    certificate_date = fields.Date(
        string="Certificate Date",
        help="Certificate Delivery Date",
        required=False,
    )
    professional_experience = fields.Text(
        string="Professional Experience", required=False
    )
    turnover_minimum = fields.Monetary(string="Minimum Turn-Over")
    origin_status_id = fields.Many2one(
        "hr.origin.status", string="Origin Status", required=False
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super(Applicant, self).onchange_partner_id()
        self.title = self.partner_id.title
        if self.partner_id.origin_status_id:
            self.origin_status_id = self.partner_id.origin_status_id
        return res

    @api.multi
    def create_employee_from_applicant(self):
        employee_action_window = super().create_employee_from_applicant()
        # note: this function does not use `ensure_one`. It returns the
        # action window on the last created employee.

        for applicant in self:
            employee = applicant.emp_id
            employee.work_phone = applicant.partner_phone
            employee.mobile_phone = applicant.partner_mobile
            employee.work_email = applicant.email_from
            employee.department_id = applicant.department_id
            employee.certificate_id = applicant.type_id
            employee.certificate_date = applicant.certificate_date
            employee.professional_experience = (
                applicant.professional_experience
            )
            employee.equipment = applicant.equipment
            employee.turnover_minimum = applicant.turnover_minimum
            if applicant.partner_id:
                employee.title = applicant.partner_id.title
                employee.origin_status_id = (
                    applicant.partner_id.origin_status_id
                )
            else:
                employee.title = applicant.title
                employee.origin_status_id = applicant.origin_status_id

        return employee_action_window
