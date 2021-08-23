odoo.define('hr_attendance_ext', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var DashboardAttendance = Widget.extend({
	template: 'DashboardAttendance',

	init: function(){		
		this.all_dashboards = ['emp', 'empinfo', 'analysis'];
		return this._super.apply(this, arguments);
	},

	start: function(){
		return this.load(this.all_dashboards);
	},

	load: function(dashboards){
		var self = this;
		var loading_done = new $.Deferred();
		this._rpc({
			route: '/attendance_dashboard/data', 
			params: {
				userid: 0,
			},
			})
			.then(function (data) {
				// Load each dashboard
				var all_dashboards_defs = [];
				_.each(dashboards, function(dashboard) {
					var dashboard_def = self['load_' + dashboard](data);
					if (dashboard_def) {
						all_dashboards_defs.push(dashboard_def);
					}
				});

				// Resolve loading_done when all dashboards defs are resolved
				$.when.apply($, all_dashboards_defs).then(function() {
					loading_done.resolve();
				});
			});		
		return loading_done;
	},
	
	load_emp: function(data){
		return  new DashboardAttUser(this, data.emp).replace(this.$('.o_attendance_dashboard_emp'));
	},

	load_empinfo: function(data){
		return  new DashboardAttUsers(this, data.empinfo).replace(this.$('.o_attendance_dashboard_empinfo'));
	},

	load_analysis: function(data){
		return new DashboardAttAnalysis(this, data.empinfo).replace(this.$('.o_attendance_dashboard_analysis'));
	},
	
});

var DashboardAttUser = Widget.extend({
	template: 'DashboardAttUser',

	events: {
		'click .o_analyze_button': 'on_analyze_button',		
	},

	init: function(parent, data){
		this.data = data;
		this.parent = parent;
		return this._super.apply(this, arguments);
	},

	start: function() {
		this._super.apply(this, arguments);
				
	},

	on_analyze_button: function(){
		var self = this;
		var dashboards = ['empinfo', 'analysis'];
		var uid = $("#userid").val();
    	//alert(uid);
		var loading_done = new $.Deferred();
		this._rpc({
			route: '/attendance_dashboard/data', 
			params: {
				userid: uid,
			},
			})
			.then(function (data) {
			// Load each dashboard
			var all_dashboards_defs = [];
			_.each(dashboards, function(dashboard) {
				var dashboard_def = self.parent['load_' + dashboard](data);
				if (dashboard_def) {
				    all_dashboards_defs.push(dashboard_def);
				}
			});

			// Resolve loading_done when all dashboards defs are resolved
			$.when.apply($, all_dashboards_defs).then(function() {
				loading_done.resolve();
			});
		});
		return loading_done;
		//this.do_action('base.open_module_tree');
	},
	
});

var DashboardAttUsers = Widget.extend({
	template: 'DashboardAttUsers',
	
	init: function(parent, data){
		this.data = data;
		this.parent = parent;
		return this._super.apply(this, arguments);
	},	
	reload:function(){
		return this.parent.load(['userinfo']);
	},
});


var DashboardAttAnalysis = Widget.extend({
	template: 'DashboardAttAnalysis',
	
	init: function(parent, data){
		this.data = data;
		this.parent = parent;
		return this._super.apply(this, arguments);
	},
	
	reload:function(){
		return this.parent.load(['userinfo']);
	},
});

core.action_registry.add('attendance_dashboard.main', DashboardAttendance);

return {
    DashboardAttendance: DashboardAttendance,
    DashboardAttUsers: DashboardAttUsers,
    DashboardAttAnalysis: DashboardAttAnalysis,
};

});
