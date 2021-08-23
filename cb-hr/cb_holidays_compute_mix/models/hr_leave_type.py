# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    exclude_rest_days = fields.Boolean(
        string="Exclude Rest Days",
        help="If enabled, the employee's day off is skipped in leave days "
        "calculation.",
    )

    company_id = fields.Many2one(default=False)
    description = fields.Text()

    validation_type = fields.Selection(default="both")
