# -*- encoding: utf-8 -*-

{
    'name': 'QPR CRM Customization',
    'category': 'Sales',
    'version': '1.0',
    'depends': ['sale_crm'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'wizard/views.xml',

        'views/crm_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
