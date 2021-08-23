# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Base Profile',
 'version': '10.0.0.1.0',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """
    This module will install the minimal necessary to extend the base module
 """,
 'depends': [
     'document',

     # https://github.com/akretion/odoo-usability
     'base_usability',
     'mail_usability',
     'base_company_extension',
     'partner_tree_default',
     'base_partner_ref',
     # optionnal
     #'eradicate_quick_create', be careful have ui issue with project

     # https://github.com/OCA/server-tools
     'base_technical_features',
     'scheduler_error_mailer',
     'disable_odoo_online',

     # https://github.com/OCA/web
     'web_sheet_full_width',
     'web_export_view',
     'web_translate_dialog',
 ],
 'installable': True,
 'application': True,
 }



