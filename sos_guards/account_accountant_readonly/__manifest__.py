{
    'name': 'Add Read-Only Accountant Group',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
Overview:
===============================

* Odoo does not come with a read-only accountant group out of the box, which is inconvenient when you need to have an external accountant go through your accounting records in Odoo.  This module adds a group 'Accountant Read-Only' so it's easy to grant an external accountant access to your Odoo system.
* This group inherits the group 'Employee', thus minimum level of create/write/delete rights will be granted for some non-accounting related models. 
    """,
    'author': 'Farooq Arif',
    'website': 'http://www.aarsol.com',
    'license': 'AGPL-3',
    'depends': [],
    'data': [
#        'security/account_security.xml',
#        'security/ir.model.access.csv',
        ],
    'installable': True,
    'application': False,
    'auto_install': False, 
}

