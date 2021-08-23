# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging

import phonenumbers

from odoo import api, models

_logger = logging.getLogger(__name__)


def _format_phone_number(number):
    number = phonenumbers.parse(number, "FR")
    if number.country_code == 33:
        return phonenumbers.format_number(
            number, phonenumbers.PhoneNumberFormat.NATIONAL
        )
    else:
        return phonenumbers.format_number(
            number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, values):

        if "mobile_phone" in values and values["mobile_phone"]:
            values["mobile_phone"] = _format_phone_number(
                values["mobile_phone"]
            )
        if "work_phone" in values and values["work_phone"]:
            values["work_phone"] = _format_phone_number(values["work_phone"])

        employee = super().create(values)
        return employee

    @api.multi
    def write(self, values):
        if "mobile_phone" in values and values["mobile_phone"]:
            values["mobile_phone"] = _format_phone_number(
                values["mobile_phone"]
            )
        if "work_phone" in values and values["work_phone"]:
            values["work_phone"] = _format_phone_number(values["work_phone"])
        return super().write(values)
