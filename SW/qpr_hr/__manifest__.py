# -*- coding: utf-8 -*-

{
    'name': 'QPR HR Changes',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        This Module add below functionality into Odoo

        1. This module helps you to display unique Employee Number on Employee Form
        2. Employee No. Will be Fixed for Approved Employees. 
        3.

    """,
    'summary': 'Various Changes on HR Modules',
    'depends': ['hr', 'hr_holidays'],
    'data': [

        'security/security.xml',
        'security/ir.model.access.csv',

        'wizard/warning.xml',

        'views/employee_sequence.xml',
        'views/employee_view.xml',
        'views/hr_holidays_views.xml',
        'views/air_ticket_request_views.xml',
        'views/trip_request_views.xml',
        'views/hr_leave_type_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',

        'data/mail_data.xml',
        'data/ir_sequence_data.xml',
    ],
    'demo': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'author': 'QPR Qatar',
    'website': 'http://www.qpr.qa',
}
