# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Accounting Fr Profile',
 'version': '10.0.0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Profile Modules',
 'description': """
    This module is a generic profile for accounting.
 """,
 'depends': [
     'profile_accounting',

     # https://github.com/OCA/l10n-france
     'l10n_fr',
     'l10n_fr_siret',
 ],
 'data': [
 ],
 'installable': True,
 'application': True,
 }
