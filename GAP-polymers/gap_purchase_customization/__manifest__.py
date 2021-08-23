# -*- coding: utf-8 -*-
{
    'name': "GAP Purchase Customization",

    'summary': """
        GAP Purchase Customization """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'purchase',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/purchase_order.xml',
    ],



}