# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Sale List View",
    "summary": """
      Shows sales for each product. """,
    "author": "Quartile Limited, Timeware Limited",
    "category": "Product",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale_mto_order_lines", "product_local_oversea_stock_info"],
    "data": [
        "data/ir_actions.xml",
        "views/product_template_views.xml",
        "views/sale_order_line_views.xml",
    ],
    "installable": True,
}
