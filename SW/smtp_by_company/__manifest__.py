# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

{
    'name': 'SMTP BY COMPANY',
    'description':"""Customised module which allows to configure
            outgoing email server by company.
                """,
    "version": "12.0.0.1.0",
    'category': 'Mail',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'license': 'AGPL-3',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'https://www.jupical.com',
    'depends': ['mail'],
    'summary':'Configure different outgoing mail server for each company',
    'data': ['views/ir_mail_server_view.xml'],
    'installable': True,
    'images':['static/description/poster_image.png'],
    'price': 18.00,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: