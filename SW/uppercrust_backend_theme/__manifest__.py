# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

{
    'name': 'Uppercrust Backend Theme',
    'category': "Themes/Backend",
    'version': '1.2.2',
    'license': 'OPL-1',
    'summary': 'Customized Backend Theme',
    'description': 'Customized Backend Theme',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'depends': ['document'],
    'website': 'www.synconics.com',
    'data': [
        'data/theme_data.xml',
        'security/global_search_security.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/webclient_templates.xml',
        'views/global_search_config_view.xml',
        'wizard/global_search_batch_wizard_view.xml',
        'views/global_search_config_batch_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/main_screen.png',
        'static/description/uppercrust_screenshot.jpg',
    ],
    'price': 449.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'bootstrap': True,
    'application': True,
}
