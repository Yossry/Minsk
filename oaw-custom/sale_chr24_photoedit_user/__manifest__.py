# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale group for Chrono24 and Products",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited, Timeware Limited",
    "website": "",
    "depends": ["sale_chr24"],
    "summary": """
    A group for managing Chrono24 information and managing photos of products.
    """,
    "data": [
        "security/chr24_photoedit_security.xml",
        "views/product_product.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
