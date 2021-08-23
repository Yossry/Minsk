# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Internal Warehouse',
    'version': '12.0.1.1.0',
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Ventor Internal Warehouse',
    'depends': [
        'merp_base',
    ],
    'data': [
        'views/res_users.xml',
        'views/stock_warehouse.xml',
    ],
}
