# Copyright 2019 Quartile Limted, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock View Adjust",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock",
        "sale_order_line_quant",
        "stock_picking_menu",
        "stock_move_line_quant",
    ],
    "data": [
        "data/ir_actions.xml",
        "security/ir.model.access.csv",
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
    ],
}
