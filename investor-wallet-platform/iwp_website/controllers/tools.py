# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#     Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request


def monetary_to_text(value, currency=None):
    if currency is None:
        currency = (
            request.env['res.company']._company_default_get().currency_id
        )
    value_to_html = request.env['ir.qweb.field.monetary'].value_to_html
    html_val = value_to_html(float(value), {"display_currency": currency})
    raw_val = (
        html_val
        .replace('<span class="oe_currency_value">', "")
        .replace("</span>", "")
    )
    return raw_val

