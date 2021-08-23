# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Person (Aux)',
    'summary': 'Person (Aux) Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
        'clv_global_log',
        'clv_partner_entity',
        'clv_person',
        'clv_address_aux',
        'clv_family_aux',
    ],
    'data': [
        'security/person_aux_security.xml',
        'security/ir.model.access.csv',
        'views/person_aux_view.xml',
        'views/person_aux_log_view.xml',
        'views/aux_instance_view.xml',
        'views/person_aux_marker_view.xml',
        'views/person_aux_category_view.xml',
        'views/res_partner_view.xml',
        'views/global_tag_view.xml',
        'views/address_view.xml',
        'views/family_view.xml',
        'views/person_view.xml',
        'views/address_aux_view.xml',
        # 'views/family_aux_view.xml',
        'wizard/person_aux_mass_edit_view.xml',
        'wizard/person_aux_contact_information_updt_view.xml',
        'wizard/person_associate_to_person_aux_view.xml',
        'wizard/person_aux_associate_to_address_view.xml',
        'wizard/person_aux_associate_to_address_aux_view.xml',
        'wizard/person_aux_associate_to_family_view.xml',
        # 'wizard/person_aux_associate_to_family_aux_view.xml',
        'wizard/person_aux_associate_to_related_person_family_view.xml',
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