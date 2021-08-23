# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Vendor Consignment Stock",
    "summary": "Manage stock in our warehouse that is owned by a vendor",
    "version": "12.0.1.0.0",
    "author": "Camptocamp," "Quartile Limited," "Odoo Community Association (OCA),",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "stock_ownership_availability_rules",
        "sale_owner_stock_sourcing",
        "sale_stock",
        "purchase_order_line_quant",
        "purchase_stock",
    ],
    "data": [
        "data/vendor_consignment_stock_data.xml",
        "views/stock_warehouse_views.xml",
        "views/purchase_order_views.xml",
    ],
    "post_init_hook": "workaround_create_initial_rules",
    "auto_install": False,
    "installable": True,
}
