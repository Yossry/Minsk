# -*- coding: utf-8 -*-
{
    'name': "Vendor Bill By Product Category",

    'summary': """
        Vendor Bill By Product Category """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'Purchase',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase','account'],

    # always loaded
    'data': [
        'wizard/purchase_invoice_category_wizard.xml',
        'views/purchase_order.xml',
    ],



}