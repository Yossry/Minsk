# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Quant Custom Transfer",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.odoo-asia.com",
    "category": "Warehouse",
    "license": "AGPL-3",
    "summary": """Create custom transfer from quant""",
    "depends": ["sale_stock", "stock_move_line_quant"],
    "data": ["wizard/stock_quant_transfer_wizard.xml"],
    "installable": True,
    "application": False,
}
