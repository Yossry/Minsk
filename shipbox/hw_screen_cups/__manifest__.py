# -*- coding: utf-8 -*-
{
    'name': 'Screen Driver with CUPS',
    'version': '1.0',
    'category': 'Hardware Drivers',
    'author': 'Hibou Corp.',
    'sequence': 7,
    'summary': 'Provides list of attached print queues.',
    'website': 'https://www.odoo.com/page/point-of-sale',
    'description': """
Screen Driver with CUPS
=======================

This module adds a list of configured CUPS printers to the 
status page.
""",
    'depends': ['hw_screen'],
    'installable': False,
    'auto_install': False,
}
