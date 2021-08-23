# -*- coding: utf-8 -*-

{
    'name': 'CUPS Print Queue Hardware Driver',
    'category': 'Point of Sale',
    'author': "Hibou Corp.",
    'license': 'AGPL-3',
    'sequence': 6,
    'summary': 'Endpoint for print queues.',
    'website': 'https://www.odoo.com/page/point-of-sale',
    'description': """
CUPS Print Queue Hardware Driver
================================

This module exposes a CUPS compatible printer in a queue.  This is specifically engineered 
to provide binary support for ZPL printing to Zebra printers, however it works across any CUPS print queue.

Setup
=====

Create a CUPS print queue named `default`.  This will be the primary device, unless otherwise specified.

""",
    'depends': ['hw_proxy'],
}
