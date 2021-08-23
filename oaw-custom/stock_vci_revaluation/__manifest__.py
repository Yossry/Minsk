# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock VCI Revaluation",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "website": "https://www.quartile.co",
    "author": "Quartile Limited",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_order_line_quant"],
    "data": [
        "data/stock_vci_revaluation_data.xml",
        "wizards/stock_vci_revaluation_wizard_views.xml",
    ],
}
