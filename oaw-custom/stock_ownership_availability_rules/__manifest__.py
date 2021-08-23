# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Ownership Availability Rules",
    "summary": "Enforce ownership on stock availability",
    "version": "12.0.1.0.0",
    "author": "Camptocamp," "Quartile Limited," "Odoo Community Association (OCA),",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": ["stock"],
    "demo": [],
    "data": [
        "security/stock_ownership_availability_rules_security.xml",
        "views/stock_move_views.xml",
    ],
    "auto_install": False,
    "installable": True,
}
