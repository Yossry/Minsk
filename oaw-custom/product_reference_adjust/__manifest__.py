# Copyright 2019 Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product representation by name and code",
    "summary": """
        Redefines product representation in various views.
    """,
    "license": "AGPL-3",
    "author": "Timeware Limited",
    "category": "Products",
    "version": "12.0.1.0.0",
    "depends": [
        "account_invoice_line_view_oaw",
        "purchase",
        "stock_view_adjust_oaw",
        "supplier_stock",
    ],
    "data": [
        "views/account_invoice_line_views.xml",
        "views/account_invoice_views.xml",
        "views/purchase_order_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
        "views/supplier_stock_views.xml",
    ],
    "installable": True,
}
