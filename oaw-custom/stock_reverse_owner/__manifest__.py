# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Return Shipment Process",
    "summary": "Ownership Change Return Shipment Process",
    "version": "12.0.1.0.0",
    "website": "https://www.quartile.co/",
    "author": "Quartile Limited",
    "license": "AGPL-3",
    "depends": ["stock_account", "sale_order_line_quant"],
    "data": [
        "data/stock_location_data.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_return_picking_views.xml",
    ],
    "application": False,
}
