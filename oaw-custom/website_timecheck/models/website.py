# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime

from odoo import fields, models
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Website(models.Model):
    _inherit = "website"

    homepage_url = fields.Char(
        string="Homepage",
        help="Defines the homepage for the website, leave it empty to be set "
        "as default ('/')",
    )

    def sale_product_domain(self):
        domain = super(Website, self).sale_product_domain()
        new_arrival_date = (
            datetime.datetime.now() + datetime.timedelta(days=-7)
        ).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if request.session.get("new_arrival"):
            domain.append(("stock_new_arrival", ">=", new_arrival_date))
        elif request.session.get("special_offer"):
            if not self.env.user.has_group("website_timecheck.group_timecheck_light"):
                domain.extend(
                    (
                        ("sale_hkd_ac_so", "!=", 0),
                        (
                            "special_offer_limit",
                            "<=",
                            datetime.datetime.now().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                    )
                )
            else:
                domain.append(("sale_hkd_ac_so", "!=", 0))
        if request.session.get("hk_stock"):
            domain.append(("local_stock_not_reserved", ">", 0))
        elif request.session.get("oversea_stock"):
            domain.append(("qty_overseas", ">", 0))
        return domain
