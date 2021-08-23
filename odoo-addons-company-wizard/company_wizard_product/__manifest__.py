# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Company Wizard - Product Module',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'summary': "Glue module to create companies when Product module is"
    " installed",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'company_wizard_base',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/res_groups.xml',
    ],
    'installable': True,
    'auto_install': True,
}
