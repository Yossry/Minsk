# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Yemen - Accounting',
    'version': '12.0.0',
    'author': 'Sonod',
    'license': 'LGPL-3',
    'category': 'Localization',
    'description': """
        Chart of Accounts - Yemen.
    """,
    'website': 'https://sonod.tech',
    
    'depends': ['account', 'l10n_multilang'],
    'data': [
        'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/l10n_ye_chart_data.xml',
        'data/account_chart_template_configure_data.xml',
    ],
    'post_init_hook': 'load_translations',
}
