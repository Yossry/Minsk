# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'WF Payment Customization',
    'summary': 'Payment Customization',
    # 'depends': ['account','om_account_asset','base','acc_pi','uom'],
    'depends': 
    ['account','account_pdc','invoice_multi_payment'],
    'data': [
        'views/test_view.xml',
        'security/ir.model.access.csv',
       
    ],
    'css': ['static/src/css/crmm.css'],
    'installable': True,
    'auto_install': False,
    'application': True,
}

