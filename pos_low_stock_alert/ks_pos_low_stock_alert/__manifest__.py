# -*- coding: utf-8 -*-
{
    'name': "POS Low Stock Alert",
    'summary': """Manage the Stock of your POS products by highlighting them in different colors depending on
                their stock state.""",
    'description': """
        POS Low Stock Alert v12.0
        Manage the Stock of your POS products by highlighting them in different colors depending on
                their stock state.
        POS
        POS Low Stock Alert
        Low Stock Alert
        Stock Alert
        POS Low Stock Warning
        POS Stock Warning
        Inventory Alert
        Inventory Minimum Quantity Alert
        Inventory Minimum Quantity Warning
        POS Manager
        POS Inventory
        POS Stock
        POS Stock Alert
        POS Retail
        POS Shop
        Point of Sales
        Point of Sales Stock Alert
        Point of Sales Low Stock Alert
        POS Shop Low Stock
    """,
    'author': 'Ksolves India Pvt. Ltd.',
    'website': "https://www.ksolves.com/",
    'license': 'LGPL-3',
    'category': 'Point Of Sale',
    'support': 'sales@ksolves.com',
    'version': '1.0.0',
    'images': ['static/description/main.jpg'],
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/config.xml'
    ],
    'qweb': ['static/src/xml/ks_low_stock.xml']
}
