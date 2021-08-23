# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrApplicant(models.Model):

    _inherit = "hr.applicant"

    firstname = fields.Char(string="First Name")
    lastname = fields.Char(string="Last Name")
    lastname2 = fields.Char(string="Second Last Name")
    partner_name = fields.Char(
        compute="_compute_applicant_name", reaonly=True, store=True
    )

    @api.depends("lastname", "lastname2", "firstname")
    def _compute_applicant_name(self):
        for record in self:
            names_list = [record.firstname, record.lastname, record.lastname2]
            name_vals = filter(lambda r: r not in ["", " ", False], names_list)
            record.partner_name = " ".join(list(name_vals)) or False

    # Overriding the function
    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            new_partner_id = self.env["res.partner"].create(
                {
                    "is_company": False,
                    "is_practitioner": True,
                    "name": applicant.partner_name,
                    "email": applicant.email_from,
                    "phone": applicant.partner_phone,
                    "mobile": applicant.partner_mobile,
                    "firstname": applicant.firstname,
                    "lastname": applicant.lastname,
                    "lastname2": applicant.lastname2,
                }
            )
            address_id = new_partner_id.address_get(["contact"])["contact"]
            if applicant.job_id and applicant.partner_name:
                applicant.job_id.write(
                    {
                        "no_of_hired_employee": (
                            applicant.job_id.no_of_hired_employee + 1
                        )
                    }
                )
                employee = self.env["hr.employee"].create(
                    {
                        "name": applicant.partner_name,
                        "job_id": applicant.job_id.id,
                        "address_home_id": address_id,
                        "partner_id": new_partner_id.id,
                        "department_id": applicant.department_id.id or False,
                    }
                )
                applicant.write({"emp_id": employee.id})
                applicant.job_id.message_post(
                    body=_("New Employee %s Hired") % applicant.partner_name
                    if applicant.partner_name
                    else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired",
                )
                # employee._broadcast_welcome()
                # TODO: Set to done Stage
            else:
                raise UserError(
                    _(
                        "You must define an Applied Job and a"
                        " Contact Name for this applicant."
                    )
                )

        employee_action = self.env.ref("hr.open_view_employee_list")
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window["res_id"] = employee.id
        dict_act_window["view_mode"] = "form,tree"
        return dict_act_window
