# coding: utf-8
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Multi Company - Base Module',
    'version': '10.0.1.0.0',
    'category': 'Multi Company',
    'summary': 'Handle Multi company for Base Module',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/view_ir_property.xml',
        'views/view_ir_sequence.xml',
        'views/view_ir_values.xml',
        'views/view_res_company.xml',
        'views/view_res_partner.xml',
        'views/view_res_users.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
    ],
    'images': [
        'static/description/res_company_form.png',
    ],
    'installable': True,
}
