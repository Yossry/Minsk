# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Timecheck Function For Supplier",
    "category": "Website",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": ["website_sale_adj", "website_timecheck"],
    "summary": """""",
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/supplier_stock_views.xml",
        "views/templates.xml",
    ],
    "installable": True,
}
