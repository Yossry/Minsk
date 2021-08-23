# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ValueLog(models.Model):
    _name = "value.log"
    _description = "Value Log"

    model = fields.Char(string="Model", required=True)
    field = fields.Char(string="Field", required=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        default=lambda self: self.env.uid,
        required=True,
    )
    date = fields.Date(
        string="Date",
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    record_id = fields.Integer(string="Record Id")
    previous_value = fields.Char(string="Previous Value")
    new_value = fields.Char(string="New Value")
