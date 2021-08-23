# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_supplier_stock_search_order(self, post):
        return "readonly_record"

    def _get_supplier_stock_domain(self, supplier):
        return [("partner_id", "=", supplier), ("website_published", "=", True)]
