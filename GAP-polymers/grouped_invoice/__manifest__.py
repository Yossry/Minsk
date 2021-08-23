# -*- coding: utf-8 -*-
{
    'name': "Grouping Invoices",

    'summary': """
        Grouping Invoices """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'account',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/invoice_selection_wizard.xml',
        'views/account_invoice.xml',
        'views/account_invoice_group.xml',
        'views/account_invoice_group_report.xml',

    ],



}