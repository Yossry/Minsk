# -*- encoding: utf-8 -*-
{
    'name' : 'SW - HR Overtime Management',
    'version' : '12.0.1.0',
    'category' : 'Human Resources',
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    'license' : 'Other proprietary',
    'summary': "Manage Employees Overtime",
    'description':"",
    'data': ["data/data.xml",
             "view/hr_overtime.xml",
             'security/ir.model.access.csv',
             'view/res_config_views.xml'
             ],
    'depends' : ['base','hr','account','analytic','hr_payroll','hr_payroll_account'],
    'images':  ["static/description/image.png"],
    'price' : 50,
    'currency' :  'EUR',
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}