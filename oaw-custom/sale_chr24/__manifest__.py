# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Adds chrono24 management to Sales ",
    "category": "Products",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited, Timeware Limited.",
    "website": "",
    "depends": ["product_local_oversea_stock_info", "product_listprice_list_view"],
    "summary": """
    Adds chrono24  fields to PLV. Adds a new tree views to Sales to
    manage chrono24
    """,
    "data": [
        "data/ir_actions.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
}
