# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Exemption(models.Model):
    _name = "hr.contribution.exemption"
    _description = "Contribution Exemption"

    name = fields.Char()
    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee"
    )

    reason = fields.Text(string="Reason for Exemption", required=False)
    date_start = fields.Date(string="Start Date of Exemption", required=False)
    date_end = fields.Date(string="End Date of Exemption", required=False)

    @api.constrains("date_start", "date_end")
    def _constrain_mutual_insurance_date(self):
        for exemption in self:
            if (
                exemption.date_start
                and exemption.date_end
                and exemption.date_start > exemption.date_end
            ):
                raise ValidationError(
                    _(
                        "The start date of mutual insurance must be before the "
                        "end date"
                    )
                )
