# Copyright 2018 Xavier Piernas <xavier.piernas@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hide Commercial Name Report",
    "summary": "Hide Partner Commercial Name on Reports",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "https://www.qubiq.es",
    "author": "QubiQ, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "purchase",
        "sale",
        "stock"
    ],
    "data": [
        "reports/account_invoice.xml",
        "reports/purchase_order.xml",
        "reports/sale_order.xml",
        "reports/stock_picking.xml"
    ],
}
