odoo.define('aarsol_accounts.reconciliation', function (require) {
"use strict";

var widgets = require('account.reconciliation');
var core = require('web.core');
var Model = require('web.Model');

var _t = core._t;


widgets.abstractReconciliation.include({
	
	init: function(parent, context) {
        var self = this;
        var FieldMany2One = core.form_widget_registry.get('many2one');
        
        this._super(parent, context);
       
       /*
       	self.create_form_fields['a1_id'] = {
			id: 'a1_id',
			index: 41,
			corresponding_property: 'a1_id',
			label: _t("CC"),
			required: false,
			tabindex: 14,
			constructor: FieldMany2One,
			field_properties: {
				relation: "analytic.code",
				string: _t("CC"),
				type: "many2one",
			}
		};
		self.create_form_fields['a2_id'] = {
			id: 'a2_id',
			index: 42,
			corresponding_property: 'a2_id',
			label: _t("Partner"),
			required: false,
			tabindex: 14,
			constructor: FieldMany2One,
			field_properties: {
				relation: "analytic.code",
				string: _t("Partner"),
				type: "many2one",
			}
		};
		self.create_form_fields['a3_id'] = {
			id: 'a3_id',
			index: 43,
			corresponding_property: 'a3_id',
			label: _t("Employee"),
			required: false,
			tabindex: 14,
			constructor: FieldMany2One,
			field_properties: {
				relation: "analytic.code",
				string: _t("Employee"),
				type: "many2one",
			}
		};
		self.create_form_fields['a4_id'] = {
			id: 'a4_id',
			index: 44,
			corresponding_property: 'a4_id',
			label: _t("Department"),
			required: false,
			tabindex: 14,
			
			constructor: FieldMany2One,
			field_properties: {
				relation: "analytic.code",
				string: _t("Department"),
				type: "many2one",
			}
		};
		*/
        
        new Model("analytic.structure")
        	.call("get_dimensions_names2",['account_bank_statement_line'])
            .then(function (data) {
            	
            	var ind = 41;
            	 
            	for(var key in data) {		        	
		        	var fld = 'a'+key+'_id';
	  				var value = data[key].split("::");
		        	  self.create_form_fields[fld] = {
						id: fld,
						index: ind,
						corresponding_property: fld,
						label: _t(value[1]),
						required: false,
						tabindex: 14,
						constructor: FieldMany2One,
						field_properties: {
							relation: "analytic.code",
							string: _t(value[1]),
							type: "many2one",
							domain: [['nd_id','=',parseInt(value[0])]],
						}
					};
					ind += 1; 
            	}
            	
            });   // then
       
	},
	
});

});


