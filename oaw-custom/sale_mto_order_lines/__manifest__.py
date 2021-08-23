# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MTO Sale Order Lines",
    "category": "Sale",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited, Timeware Ltd",
    "website": "https://www.quartile.co",
    "depends": [
        "sale_order_line_quant",
        "supplier_user_access",
        "sale_view_adjust_oaw",
    ],
    "summary": """ MTO Order List views for Internal and Supplier """,
    "data": ["views/sale_order_views.xml"],
    "installable": True,
}
