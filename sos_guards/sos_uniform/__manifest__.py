{
	'name': 'SOS Store Management',
	'version': '0.1',
	'category': 'Security Guards System',
	'license': 'AGPL-3',
	'description': "This module is for Issurance of Uniform to SOS Guards",
	'author': 'Farooq',
	'website': 'http://www.aarsolerp.com/',
	'depends': ['account','sos','stock'],
	'init_xml': [],
	'data': [
    	
    	'security/sos_security.xml',
		'security/ir.model.access.csv',
		'data/sos_uniform_data.xml',
		'views/sos_stock_view.xml',         

		'views/sos_uniform_view.xml',
		'views/sos_jacket_view.xml',
		'views/sos_weapon_view.xml',
		'views/sos_stationery_view.xml',
		'views/sos_safety_view.xml',
		'views/sos_button_inventory_view.xml',
		'views/sos_button_inventory_issuance_view.xml',
		'views/sos_pack_operation_view.xml',
		'views/sos_damage_demand_view.xml',

		'sos_uniform_return/sos_uniform_return_view.xml',
		'views/sos_approval_view.xml',

		'wizard/uniform_report_wizard_view.xml',
		'wizard/jacket_report_wizard_view.xml',
		'wizard/weapon_report_wizard_view.xml',
		'wizard/stationery_report_wizard_view.xml',

		'wizard/sos_safety_stock_wizard_view.xml',
		'wizard/sos_uniform_safety_usage_wizard_view.xml',
		'wizard/sos_purchase_rep_wizard_view.xml',

		  
        'wizard/stock_wizards/daily_stock_wizard_view.xml',
        'wizard/stock_wizards/uniform_wizard_view.xml',
        'wizard/stock_wizards/shoes_wizard_view.xml',
        'wizard/stock_wizards/accessories_wizard_view.xml',
        'wizard/stock_wizards/weapon_wizard_view.xml',
        'wizard/stock_wizards/ammunition_wizard_view.xml',
        'wizard/stock_wizards/stationary_wizard_view.xml',
        'wizard/stock_wizards/lady_uniform_wizard_view.xml',
        'wizard/stock_wizards/trouser_wizard_view.xml',
        'wizard/stock_wizards/tshirt_wizard_view.xml',
        
		'report/report_uniform.xml',
		'report/report_uniform_center_all.xml',
		'report/report_uniform_center_specific.xml',
		'report/report_uniform_project_all.xml',
		'report/report_uniform_project_specific.xml',
		'report/report_uniform_post_all.xml',
		'report/report_uniform_post_specific.xml',

		'report/report_weapon.xml',
		'report/report_weapon_project_all.xml',
		'report/report_weapon_project_specific.xml',
		'report/report_weapon_center_all.xml',
		'report/report_weapon_center_specific.xml',
		'report/report_weapon_post_all.xml',
		'report/report_weapon_post_specific.xml',

		'report/report_jacket.xml',
		'report/report_jacket_center_all.xml',
		'report/report_jacket_center_specific.xml',
		'report/report_jacket_project_all.xml',
		'report/report_jacket_project_specific.xml',
		'report/report_jacket_post_all.xml',
		'report/report_jacket_post_specific.xml',

		'report/report_stationery.xml',
		'report/report_safetystock.xml',
		'report/report_safetyusage.xml',
		'report/report_purchase.xml',

		'report/report_uniformdemand.xml',
		'report/report_weapondemand.xml',
		'report/report_jacketdemand.xml',
		'report/report_stationerydemand.xml',
		'report/report_safetydemand.xml',

		'report/stock_reports/report_dailystock.xml',
        'report/stock_reports/report_uniform.xml',
        'report/stock_reports/report_shoes.xml',
        'report/stock_reports/report_accessories.xml',
        'report/stock_reports/report_weapon.xml',
        'report/stock_reports/report_ammunition.xml',
        'report/stock_reports/report_stationary.xml',
        'report/stock_reports/report_ladyuniform.xml',
        'report/stock_reports/report_trouser.xml',
        'report/stock_reports/report_tshirt.xml',        
        

		'report/report.xml',
		'report/stock_reports/report.xml',
		'menu/uniform_menu.xml',
		
	],
	'demo_xml': [],
	'installable': True,
	'application' : True,
}


