
{
    'name': 'Assets',
    'version': '1.9',
    'summary': 'Asset Management',
    'description': """
Managing Assets in Odoo.
===========================
Support following feature:
    * Location for Asset
    * Assign Asset to employee
    * Track warranty information
    * Custom states of Asset
    * States of Asset for different team: Finance, Warehouse, Manufacture, Maintenance and Accounting
    * Drag&Drop manage states of Asset
    * Asset Tags
    * Search by main fields

Integrate financial and maintenance asset management.
===========================

This module allows use the same Assets for maintenance and accounting purposes.
Keep one entity in one place for escape mistakes!

Track all Asset Hystory in Odoo.
===========================
Support following feature:
    * Track changes in all fields

Integrate Maintenance and Purchase.
===========================

This module allows use the same Assets for purchase and maintenance purposes.
Keep one entity in one place for escape mistakes!

Integrate Maintenance and Sale.
===========================

This module allows use the same Assets for sale and maintenance purposes.
Keep one entity in one place for escape mistakes!

Integrate Maintenance and Warehouse.
===========================

This module allows use the same Assets for warehouse and maintenance purposes.
Keep one entity in one place for escape mistakes!

    """,
    'author': 'Farooq Arif',
    'website': 'http://codup.com',
    'category': 'Enterprise Asset Management',
    'sequence': 0,
    'images': ['images/assets.png'],
    'depends': ['purchase','stock','account_asset','analytic_structure'],
    'demo': ['asset_demo.xml'],
    'data': [
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        'asset_view.xml',
        'asset_data.xml',
        'stock_data.xml',
        'views/asset.xml',
		#'purchase_view.xml',
		#'sale_view.xml',
		#'stock_view.xml',
    ],
    'installable': True,
    'application': True,
}

