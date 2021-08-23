# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Quant/Serial Number on Sales",
    "category": "Sale",
    "version": "12.0.1.0.1",
    "license": "LGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": [
        "stock",
        "sale_margin",
        "stock_move_line_quant",
        "sale_owner_stock_sourcing",
    ],
    "summary": """ Serial Number Quant on Sales Order Line""",
    "data": ["views/sale_order_views.xml"],
    "installable": True,
}
