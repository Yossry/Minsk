# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
#################################################################################
{
  "name"                 :  "Odoo Vendor Portal",
  "summary"              :  """The module allows you to provide a website portal to the vendors so they can track and manage purchase orders directly from their account.""",
  "category"             :  "Website",
  "version"              :  "1.0.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo-Vendor-Portal.html",
  "description"          :  """Odoo Vendor Portal
Odoo vendor account on website
Odoo vendor website account
Manage purchase order from vendor account""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_vendor_portal&version=12.0&lout=1&custom_url=/",
  "depends"              :  [
                             'purchase',
                             'website',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/ir_sequence_data.xml',
                             'data/data.xml',
                             'data/mail_template_data.xml',
                             'wizard/vendor_login_account_view.xml',
                             'wizard/vendor_rfq_done_view.xml',
                             'views/res_config_views.xml',
                             'views/res_partner_view.xml',
                             'views/vendor_rfq_view.xml',
                             'views/vendor_rfq_history_view.xml',
                             'views/vendor_rfq_template.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}