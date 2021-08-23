# -*- coding: utf-8 -*-
{
    'name': 'Todoo Partner Customization',
    'version': '12.0.1.2',
    'author': "Moogah",
    'website': "www.moogah.com",
    'category': '',
    'depends': [
        'l10n_co_edi',
        'account',
        'contacts',
        'sale_management',
        'purchase',

    ],
    'data': [
        'security/ir.model.access.csv',
        'views/address_code_views.xml',
        'views/street_code_views.xml',
        'views/ciiu_value_views.xml',
        'views/partner_views.xml',
        'wizard/res_partner_wizard_views.xml',
    ],
    'installable': True
}
