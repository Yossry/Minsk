odoo.define('salary.planner', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var rpc = require('web.rpc');
var planner = require('wizard.planner');
var session = require('web.session');

var QWeb = core.qweb;
var _t = core._t;

planner.WizardPlanner.include({
	init: function(parent, planner) {
        this._super(parent,planner);       
        this.action_manager = this.findAncestor(function(ancestor){ return ancestor instanceof ActionManager });
    },    
    prepare_planner_event: function() {
        var self = this;
        this._super.apply(this, arguments);       
        if(self.planner['planner_application'] == 'planner_salary') {
        
        	self.$('#view_contracts').on('click', function(ev) {	            	
				ev.preventDefault();								
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_contracts',
					args: [self.rec], 
					context: session.user_context,
				})        
				 .then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});
			
			self.$('#view_contracts2').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_contracts2',
					args: [self.rec], 
					context: session.user_context,
				})    				
				.then(function(result){
                	self.action_manager.do_action(result);
                });            	
			});	
			
			
			self.$('#alerts_view').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_alerts',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){                	
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});	
			
			self.$('#alerts_recalc').on('click', function(ev) {
                rpc.query({
					model: 'hr.payroll.period',
					method: 'do_recalc_alerts',
					args: [self.rec], 
					context: session.user_context,
				})    
                .then(function(result){
		            self.action_manager.do_action(
		            	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );});      
            });	
            
            self.$('#daily_to_month').on('click', function(ev) {
                rpc.query({
					model: 'hr.employee.month.attendance',
					method: 'daily_to_month',
					args: [[self.rec],[self.rec]],    // 
					context: session.user_context,
				})    
                .then(function(result){
		            self.action_manager.do_action(
		            	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );});      
            });
            
            
             self.$('#post_overtime').on('click', function(ev) {
                rpc.query({
					model: 'hr.payroll.period',
					method: 'overtime_to_inputs',
					args: [[self.rec],[self.rec]],    // 
					context: session.user_context,
				})    
                .then(function(result){
		            self.action_manager.do_action(
		            	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );});      
            });
            
            
            self.$('#import_month_attendance').on('click', function(ev) {
                ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_monthly_attendance',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });                
            });
            
            self.$('#view_month_attendance').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_monthly_attendance',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});
			
			self.$('#view_month_inputs').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_monthly_inputs',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});
			
			
			self.$('#import_month_inputs').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_monthly_inputs',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});
			
			self.$('#unlock_period').on('click', function(ev) {	            	
				ev.preventDefault();
				rpc.query({
					model: 'hr.payroll.period',
					method: 'set_state_unlocked',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
		            self.action_manager.do_action(
		            	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );});   	
			});
			
			self.$('#lock_period').on('click', function(ev) {	            	
				ev.preventDefault();
				rpc.query({
					model: 'hr.payroll.period',
					method: 'set_state_locked',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
		            self.action_manager.do_action(
		            	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );});
			});
			
			self.$('#create_payroll_register').on('click', function(ev) {	            	
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'create_payroll_register',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });            	
			});
			
			
			self.$('#view_payroll_register').on('click', function(ev) {	            					
				ev.preventDefault();
				return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_payroll_register',
					args: [self.rec], 
					context: session.user_context,
				})    
				.then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                		{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);}});
                });
			});
			
			
			self.$('#view_payroll_batch').on('click', function(ev) {                   
                ev.preventDefault();
                return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_payroll_batch',
					args: [self.rec], 
					context: session.user_context,
				})
                .then(function(result){
                    self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                    );}});
                });               
            });
            
            
		    self.$('#view_payslips').on('click', function(ev) {                   
		        ev.preventDefault();
		        return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_payslips',
					args: [self.rec], 
					context: session.user_context,
				})
	  			.then(function(result){
		            self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
		                {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
		            );}});
		        });               
		    }); 
			
			
		 self.$('#inter_transfer_salary').on('click', function(ev) {
            rpc.query({
					model: 'hr.payroll.period',
					method: 'inter_transfer_salary',
					args: [self.rec], 
					context: session.user_context,
				})
            	.then(function(result){
            		self.action_manager.do_action(
                    	{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                	);});     
        	});
        	
        	self.$('#view_inter_transfer').on('click', function(ev) {                   
                ev.preventDefault();
                return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_inter_transfer',
					args: [self.rec], 
					context: session.user_context,
				})
                .then(function(result){
                	self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                    );}});
                });               
            });
            
            self.$('#view_payroll_exceptions').on('click', function(ev) {                   
            	ev.preventDefault();
           		return rpc.query({
					model: 'hr.payroll.period',
					method: 'view_payroll_exceptions',
					args: [self.rec], 
					context: session.user_context,
				})
               .then(function(result){
					self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                    );}});
                });               
            });
            
            self.$('#start_payments').on('click', function(ev) {
            	 rpc.query({
					model: 'hr.payroll.period',
					method: 'start_payments',
					args: [self.rec], 
					context: session.user_context,
				})
				.then(function(result){
					self.action_manager.do_action(
                        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                    );});     
            });
            
            
         self.$('#summary_payslips').on('click', function(ev) {                   
            ev.preventDefault();
            return rpc.query({
				model: 'hr.payroll.period',
				method: 'summary_payslips',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
                self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
                    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
                );}});
            });               
        });
        
		self.$('#print_payroll_summary').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_summary',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
					{'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		self.$('#print_payroll_register').on('click', function(ev) {
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_register',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				    );}});
				});               
			});
	
		self.$('#print_payslip_details').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payslip_details',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				    );}});
				});               
			});
            
		self.$('#print_contribution_registers').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_contribution_registers',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});	
			
			
		self.$('#print_payroll_sheet').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_3',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){                   
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});                 
		});
            
            
		self.$('#print_payroll_sheet_1').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_1',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		self.$('#print_payroll_sheet_3').on('click', function(ev) {
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_3',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){                   
				    self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				    );}});
				});               
			});
		
		
		self.$('#print_payroll_sheet_4').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_4',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){                   
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});         
		});
		
		self.$('#print_payroll_sheet_5').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_5',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				    self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				        {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				    );}});
				});               
			});
		
		self.$('#print_payroll_sheet_6').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_sheet_6',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		self.$('#make_excel_1').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'make_excel_1',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		
		self.$('#print_payroll_accounts_1').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_accounts_1',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		
		
		self.$('#print_payroll_accounts_3').on('click', function(ev) {
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_accounts_3',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){                   
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		
		self.$('#print_payroll_accounts_4').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_accounts_4',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){                   
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});         
		});
		
		
		self.$('#print_payroll_accounts_5').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_accounts_5',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
		
		
		self.$('#print_payroll_accounts_6').on('click', function(ev) {                                   
			ev.preventDefault();
			return rpc.query({
				model: 'hr.payroll.period',
				method: 'print_payroll_accounts_6',
				args: [self.rec], 
				context: session.user_context,
			})
			.then(function(result){
				self.action_manager.do_action(result,{on_reverse_breadcrumb: function(){ self.action_manager.do_action(
				    {'type': 'ir.actions.client','name':'Salary Planner','tag':'wizard_planner_main','context':{'active_id': self.rec}},{clear_breadcrumbs:true}
				);}});
			});               
		});
			
		}
	}

});


});



