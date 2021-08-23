# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):

    _inherit = "hr.leave.type"

    extendable = fields.Boolean(string="Modifiable")
