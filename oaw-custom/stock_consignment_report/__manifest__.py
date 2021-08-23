# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Consignment Report",
    "summary": "",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "website": "https://www.quartile.co",
    "author": "Quartile Limited",
    "license": "AGPL-3",
    "depends": ["sale_order_line_quant", "stock_reverse_owner", "abstract_report_xlsx"],
    "data": [
        "reports/reports.xml",
        "wizards/stock_consignment_report_wizard_views.xml",
        "views/stock_views.xml",
    ],
    "application": False,
    "installable": True,
}
