# -*- coding: utf-8 -*-

{
    'name': 'USB Weighing Scale Hardware Driver',
    'category': 'Point of Sale',
    'author': "Hibou Corp.",
    'license': 'AGPL-3',
    'sequence': 6,
    'summary': 'USB Hardware Driver for Weighing Scales',
    'website': 'https://www.odoo.com/page/point-of-sale',
    'description': """
Weighing Scale Hardware Driver
================================

This module allows the point of sale to connect to a scale using a USB scale,
such as the Mettler Toledo PS60.

""",
    'depends': ['hw_proxy', 'hw_scale'],
    'external_dependencies': {'python': ['pyusb']},
}
