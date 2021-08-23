# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Base Profile FR',
 'version': '10.0.0.1.0',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """
    This module will install the minimal necessary to extend the base module
    for french project
 """,
 'depends': [
     'profile_base',

     # https://github.com/OCA/partner-contact
     'partner_firstname',
 ],
 'installable': True,
 'application': True,
 }



