# Copyright 2014-2015 Camptocamp SA - Yannick Vaucher, Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Owner Stock Sourcing",
    "summary": "Manage stock ownership on sale order lines",
    "version": "12.0.1.0.0",
    "author": "Camptocamp," "Quartile Limited," "Odoo Community Association (OCA),",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "website": "http://www.camptocamp.com",
    "depends": ["sale_stock", "stock_ownership_availability_rules"],
    "data": [
        "security/sale_owner_stock_sourcing_security.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
