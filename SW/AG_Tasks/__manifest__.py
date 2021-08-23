# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'sub-tasks and issue log edits',
    'author': 'Ziad Monim',
    'depends': ['base','project', 'purchase_requisition', 'stock', 'purchase', 'sale_timesheet', 'hr_timesheet', 'analytic', 'mail', 'account'],
    'data': [
        'views/view.xml',
        'views/timesheet_template_inherit.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
