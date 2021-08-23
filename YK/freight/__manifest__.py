# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
{
    'name': 'Freight Management',
    'version': '1.0',
    'category': 'freight',
    'price': 790.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website':'https://www.inteslar.com',
    'live_test_url': 'https://www.youtube.com/watch?v=66lKp26x75k&feature=youtu.be',
    'images': ['static/description/banner.jpg'],
    'author':'inteslar',
    'summary': 'Freight Management By Inteslar',
    'description': """
Key Features
------------
* Freight Management
        """,
    'depends': ['base',
                'base_setup',
                'account',
                'product',
                'web',
                'contacts',
                'mail',
                'board',
                'calendar',
                'hr'],
    'data': [
        'data/freight_data.xml',
        'security/ir.model.access.csv',
        'report/bill_of_lading.xml',
        'report/airway_bill.xml',
        'views/freight_report.xml',
        'wizard/register_invoice_freight_view.xml',
        'views/freight_view.xml',
    ],
    'qweb': [
        "static/src/xml/freight_dashboard.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}