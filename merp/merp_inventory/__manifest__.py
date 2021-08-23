# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Inventory Improvements',
    "version": "12.0.1.0.0",
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Add small improvements to Inventory Adjustment process',
    'depends': [
        'merp_base',
        'merp_custom_access_rights'
    ],
    'data': [
        'views/res_config.xml',
        'views/res_users.xml',
        'views/stock_inventory.xml',
    ],
}
