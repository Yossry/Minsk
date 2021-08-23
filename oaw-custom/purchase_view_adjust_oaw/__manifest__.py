# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase View Adjust",
    "summary": "",
    "version": "12.0.1.0.0",
    "category": "Purchase",
    "website": "https://www.quartile.co",
    "author": "Quartile Limited",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase"],
    "data": [
        "data/ir_actions.xml",
        "views/purchase_order_line_views.xml",
        "views/purchase_order_views.xml",
    ],
}
