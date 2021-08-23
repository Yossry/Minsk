odoo.define('freight_dashboard.dashboard', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var FreightDashboardView = Widget.extend(ControlPanelMixin, {
	events: _.extend({}, Widget.prototype.events, {
		'click .direct-shipment': 'direct_shipment',
        'click .house-shipment': 'house_shipment',
        'click .master-shipment': 'master_shipment',
        'click .invoices': 'action_invoice',
        'click .bills': 'action_bills',
        'click .ports': 'action_ports',
        'click #generate_payroll_pdf': function(){this.generate_payroll_pdf("bar");},
        'click #generate_attendance_pdf': function(){this.generate_payroll_pdf("pie")},
        'click .my_profile': 'action_my_profile',
	}),
	init: function(parent, context) {
        this._super(parent, context);
        var employee_data = [];
        var self = this;
        if (context.tag == 'freight_dashboard.dashboard') {
            self._rpc({
                model: 'freight.dashboard',
                method: 'get_employee_info',
            }, []).then(function(result){
                self.employee_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var freight_dashboard = QWeb.render( 'freight_dashboard.dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(freight_dashboard).prependTo(self.$el);
        self.graph();
        self.previewTable();
        return freight_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    direct_shipment: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Direct"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            src_model: 'freight.operation',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_operation': 'direct'},
            domain: [['operation','=','direct']],
            search_view_id: self.employee_data.operation_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    house_shipment: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("House"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            src_model: 'freight.operation',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_operation': 'house'},
            domain: [['operation','=','house']],
            search_view_id: self.employee_data.operation_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    master_shipment: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Master"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            src_model: 'freight.operation',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_operation': 'master'},
            domain: [['operation','=','master']],
            search_view_id: self.employee_data.operation_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_invoice: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_type': 'out_invoice'},
            domain: [['type','=','out_invoice']],
            search_view_id: self.employee_data.invoice_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_bills: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Vendor Bills"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_type': 'in_invoice'},
            domain: [['type','=','in_invoice']],
            search_view_id: self.employee_data.invoice_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_ports: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Ports"),
            type: 'ir.actions.act_window',
            res_model: 'freight.port',
            src_model: 'freight.port',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            search_view_id: self.employee_data.freight_port_search_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_my_profile: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Profile"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: self.employee_data.id,
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            context: {},
            domain: [],
            target: 'inline'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                // "October", "November", "December"],
                labels: self.employee_data.operation_labels,
                datasets: [{
                    label: 'Operations',
                    data: self.employee_data.operation_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.employee_data.operation_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.employee_data.
                            operation_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.employee_data.operation_dataset.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
        //Pie Chart
        var piectx = this.$el.find('#attendanceChart');
        bg_color_list = []
        for (var i=0;i<=self.employee_data.shipper_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.employee_data.shipper_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Attendance Pie'
                }],
                labels:self.employee_data.shipper_labels,
            },
            options: {
                responsive: true
            }
        });

    },
    previewTable: function() {
        $('#operation_details').DataTable( {
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Employee Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },
                {
                    extend: 'print',
                    exportOptions: {
                    columns: ':visible'
                    }
                },
            'colvis'
            ],
            columnDefs: [ {
                targets: -1,
                visible: false
            } ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 15,
        } );
    },
    generate_payroll_pdf: function(chart) {
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#attendanceChart');
        }

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    },
});
core.action_registry.add('freight_dashboard.dashboard', FreightDashboardView);
return FreightDashboardView
});