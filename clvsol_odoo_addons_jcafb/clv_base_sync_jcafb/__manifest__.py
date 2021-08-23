# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base External Sync (for CLVhealth-JCAFB Solution)',
    'summary': 'Base External Sync Module used in CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'base',
        'l10n_br_base',
        'clv_external_sync',
    ],
    'data': [
        'data/res_country_sync.xml',
        'data/res_country_state_sync.xml',
        'data/res_city_sync.xml',
        'data/res_users.xml',
    ],
    'demo': [],
    'test': [],
    'init_xml': [],
    'test': [],
    'update_xml': [],
    'installable': True,
    'application': False,
    'active': False,
    'css': [],
}
