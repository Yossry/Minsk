# -*- coding: utf-8 -*-
{
    'name':'Jordanian HRMS Localization',
    'version': '12.0',
    'category': 'hr',
    'summary': 'Calculate Income Tax,Social Security, and Health Insurance',
    'description': "Jordan Localization",
    'author': 'Ahmad',
    'depends': ['hr','hr_contract','hr_payroll' ,'account'],
    'data': ['views/jo_hrms_view.xml',
             'views/jo_hrms_payroll.xml',
             'data/jo_hrms_data.xml',
             'security/ir.model.access.csv',
             'security/jo_hrms_security.xml',
                ],
    'demo': ['data/jo_hrms_demo.xml'],
    'images': ["static/description/icon.png"],
    'license': "AGPL-3",
    'price':'50',
    'currency':'USD',
    'email': 'odoo.ahmad.20@gmail.com',
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

