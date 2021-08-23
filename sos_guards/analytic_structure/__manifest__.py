{
    "name": "Analytic Structure",
    "version": "12.2",
    "author": "XCG Consulting",
    "category": 'Dependency',
    'website': 'http://www.openerp-experts.com',
    "depends": [
        'base',
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'analytic_views.xml',
        'analytic_menus.xml',  #SARFRAZ
    ],
    # 'demo_xml': [],
    'css': [
        'static/src/css/analytic_structure.css',
    ],
    'test': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
