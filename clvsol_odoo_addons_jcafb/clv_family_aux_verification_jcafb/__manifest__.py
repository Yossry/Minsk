# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Family (Aux) Verification (for CLVhealth-JCAFB Solution)',
    'summary': 'Family (Aux) Verification Module used in CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_family_aux_jcafb',
        'clv_verification',
    ],
    'data': [
        'data/family_aux_verification.xml',
        'views/verification_outcome_view.xml',
        'wizard/family_aux_mass_edit_view.xml',
        'wizard/family_aux_verification_exec_view.xml',
        'wizard/family_aux_related_family_updt_view.xml',
        'wizard/family_aux_related_family_create_view.xml',
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
