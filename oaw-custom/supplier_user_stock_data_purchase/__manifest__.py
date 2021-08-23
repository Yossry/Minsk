# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Partner Stock Data Purchase",
    "category": "Stock",
    "version": "12.0.1.1.0",
    "license": "LGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": [
        "supplier_user_access",
        "product_listprice_currency",
        "quotation_report_adjust",
        "website_timecheck_supplier",
    ],
    "summary": """""",
    "data": [
        "data/ir_actions.xml",
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_data_purchase_history_views.xml",
        "views/supplier_stock_views.xml",
        "views/templates.xml",
        "wizards/purchase_supplier_stock_data_wizard_views.xml",
    ],
    "installable": True,
}
