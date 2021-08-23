# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Person History',
    'summary': 'Person History Module used in CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_person',
        'clv_phase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/person_history_view.xml',
        'views/phase_view.xml',
        'views/person_view.xml',
        'views/address_view.xml',
        'views/family_view.xml',
        'wizard/person_mass_edit_view.xml',
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
