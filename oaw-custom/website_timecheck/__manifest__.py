# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Website Timecheck Function",
    "category": "Website",
    "version": "12.0.1.2.0",
    "license": "LGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": [
        "sale_view_adjust_oaw",
        "supplier_user_access",
        "product_listprice_list_view",
        "website_sale_adj",
    ],
    "summary": """""",
    "data": [
        "data/ir_actions.xml",
        "security/timecheck_security.xml",
        "security/website_sale_security.xml",
        "views/product_product_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/sale_order_views.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "qweb": ["static/src/xml/base.xml"],
}
