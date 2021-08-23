Uppercrust Backend Theme:

Please follow below steps before install apps:
1. For customize theme we need to change permission to 777 for this file.
Give write permission for other users in below path:

/uppercrust_backend_theme/static/src/scss/variable.scss

2. Kindly configure of Global Search for related objects.
You will find this option in main menu of system.

3. Kindly configure Theme Logo & Icon on Company For Change Logo & Icon
- Go to Settings -> Companies(Select your company) Set Theme Icon & Logo on it

4. If you have purchase the theme before 19th November 2018, and following error appears:-

	Error:-
		'odoo.tools.convert.ParseError: "duplicate key value violates unique constraint "ir_config_parameter_key_uniq"
		DETAIL: Key (key)=(uppercrust_backend_theme.selected_theme) already exists.
		" while parsing /odoo_12/custom/uppercrust_backend_theme/data/theme_data.xml:121, near
		<record model="ir.config_parameter" id="default_theme">
		<field name="key">uppercrust_backend_theme.selected_theme</field>
		<field name="value" ref="uppercrust_backend_theme.theme_6"/>
		</record>'

	Solution:- 

	Please go to new terminal and apply following steps:

		-> psql your_database_name -> (apply code) delete from ir_config_parameter where key='uppercrust_backend_theme.selected_theme'; -> update your theme module.
