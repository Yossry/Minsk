{
    'name': 'AF Base Demodata',
    'version': '12.0.0.2',						
    'category': '',
    'description': """
Module to overright Odoo original demodata.
===========================================================
AFC-119

""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base'],
    'demo': [
			'data/base_partner_demo_se.xml',
            #'data/res.country.state.se.csv',
			#'data/res_company_data_se.xml',
			#'data/res_company_data_se.xml',
			#'data/res_partner_image_demo_se.xml',
			#'data/res_users_demo_se.xml'			
        ],
    'application': False,
    'installable': True,
}