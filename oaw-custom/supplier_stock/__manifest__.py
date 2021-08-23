# Copyright 2018 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Supplier Stock",
    "category": "Stock",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited, Timeware Limited",
    "website": "https://www.quartile.co",
    "depends": ["purchase", "mail", "stock"],
    "summary": """""",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/supplier_location_views.xml",
        "views/supplier_stock_views.xml",
    ],
    "installable": True,
}
