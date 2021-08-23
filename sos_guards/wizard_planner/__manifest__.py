
{
    'name': 'Wizard Planner',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
Wizard Planner
=========================

    """,
    'author': "Farooq Arif",
    'website': 'http://www.aarsol.com',
    'license': 'AGPL-3',
	'depends': [],
    'data': [    	
        'security/ir.model.access.csv',
        ##'security/ir_rule.xml',
		

		'views/wizard_planner.xml',    			
		   	
    ],
    'test': [],
   # 'qweb': ['static/src/xml/wizard_planner.xml'],
    'installable': True,
	'application': True,
}
