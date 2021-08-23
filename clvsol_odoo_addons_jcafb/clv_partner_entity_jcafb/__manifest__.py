# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Entity (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Partner Entity Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_partner_entity',
        'clv_base_jcafb',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_entity_street_pattern_view.xml',
        'views/partner_entity_menu_view.xml',
        'wizard/address_street_pattern_add_view.xml',
        'wizard/address_aux_street_pattern_add_view.xml',
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
