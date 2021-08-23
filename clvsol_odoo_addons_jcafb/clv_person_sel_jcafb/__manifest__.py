# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Person Selection (CLVhealth-JCAFB Solution)',
    'summary': 'Person Selection Module for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_address_jcafb',
        'clv_person_jcafb',
    ],
    'data': [
        'security/person_sel_security.xml',
        'security/ir.model.access.csv',
        'views/person_sel_age_group_view.xml',
        'views/person_sel_district_view.xml',
        'views/person_sel_group_view.xml',
        'views/abstract_row_view.xml',
        'views/person_sel_summary_view.xml',
        'wizard/person_sel_district_setup_view.xml',
        'wizard/person_sel_age_group_refresh_view.xml',
        'wizard/person_sel_group_setup_view.xml',
        'wizard/person_sel_group_refresh_view.xml',
        'wizard/person_sel_group_select_view.xml',
        'wizard/person_sel_summary_setup_view.xml',
        'wizard/address_selection_refresh_view.xml',
        'views/person_sel_menu_view.xml',
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
