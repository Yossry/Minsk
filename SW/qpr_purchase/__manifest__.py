# -*- encoding: utf-8 -*-

{
    'name': 'QPR Purchase Customization',
    'category': 'Purchase',
    'version': '1.0',
    'depends': ['purchase_requisition', 'hr'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'wizard/views.xml',

        'views/purchase_views.xml',
        'views/purchase_menu.xml',
        'views/partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
