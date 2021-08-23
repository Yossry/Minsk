# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################


{
    'name': 'ODOO Email CC and BCC',
    'summary': 'Add CC and BCC feature in mail',
    'category': 'Marketing',
    'version': '1.1.0',
    'sequence': 1,
    'author': "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    'website': 'https://store.webkul.com/Odoo-Email-CC-and-BCC.html',
    'description': """Add CC and BCC feature in mail,
    Email CC, Email Bcc, mail features, Email cc feature, Email Bcc features, Email CC IDs, Email BCC IDs""",
    "live_test_url":  "http://odoodemo.webkul.com/?module=odoo_email_cc_bcc&version=13.0",
    'depends': ['mail'],
    'data': [
        'views/compose_view.xml',
        'views/templates.xml',
    ],
    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "price":  35,
    "currency":  "EUR",
    "pre_init_hook":  "pre_init_check",
    'qweb': [
        'static/src/xml/thread.xml',
    ],
}
