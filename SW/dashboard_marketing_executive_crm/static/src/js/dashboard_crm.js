odoo.define("dashboard_marketing_executive_crm.dashboard_crm", function(require) {
    "use strict";
     
    var core = require("web.core");
    var dataset = require("web.data");
    var AbstractAction = require('web.AbstractAction');
    var _t = core._t;
    var QWeb = core.qweb;
    var dashboard_crm = AbstractAction.extend({
        template: 'dashboard_crm',
        formatNumber:function (num) {
            return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
        },
        start: function(){
            var self = this;
            self.fetchblocks()
        },
        events:{
            'click #get_roi_campaigns' : 'roi_campaigns_graph',
            'click #get_roi_mediums': 'roi_mediums_graph',
            'click #get_roi_sources':'roi_sources_graph',
            'click #get_lead_count_campaigns':'lead_count_campaigns',
            'click #get_lead_count_mediums':'lead_count_mediums',
            'click #get_lead_count_sources':'lead_count_sources',
        },
        fetchblocks : function(){
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_dashboard_data',
                args: [],
            }).then(function(data){
                $(".total_customers").html(data.total_customers);
                $(".total_leads").html(data.total_leads);
                $(".total_opportunities").html(data.total_opportunities);
                $(".total_expected_revenu").html(self.formatNumber(data.total_expected_revenu));
                $(".time-activity-container").html(QWeb.render("time_activity",{
                    log: data.log
                }));
                $(".user-activity-timeline-container").html(QWeb.render("user_activity_timeline",{
                    user_activity_timeline : data.user_activity_timeline
                }));
                self.roi_graph('by-roi-container',data.campaigns_by_roi);
                self.lead_per_model_count(data.lead_per_campaign);
                self.lead_trending_report(data.lead_per_stage);
                self.converted_lead(data.converted_lead)
                self.conversion_rate(data.conversion_rate)
            });
        },
        lead_trending_report : function(lead_trending_report){
            Highcharts.chart('lead-trending-report-container', {
                chart: {
                    type: 'column',
                     marginBottom: 130
                },
                title: {
                    text: ''
                },
                xAxis: {
                    categories: lead_trending_report.months,
                    title: {
                        text: 'Date'
                    },
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Lead Trending Report'
                    },
                    stackLabels: {
                        enabled: true,
                        style: {
                            fontWeight: 'bold',
                            color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                        }
                    }
                },
                legend: {
                    align: 'left',
                    itemDistance: 20,
                    verticalAlign: 'bottom',
                    floating: true,
                    backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
                    borderColor: '#CCC',
                    borderWidth: 1,
                    shadow: false,
                },
                tooltip: {
                    headerFormat: '<b>{point.x}</b><br/>',
                    pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                },
                plotOptions: {
                    column: {
                        stacking: 'normal',
                        dataLabels: {
                            enabled: true,
                            color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                        }
                    }
                },
                series: lead_trending_report.series
            });
        },
        
        lead_count_campaigns:function(){
            $(".lead_count_header").html('Lead/oppty Count per Campaign');
            $(".lead_count_footer").html('Lead/oppty Count per Campaign This Year')
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_lead_per_model',
                args: ['utm.campaign','campaign_id'],
            }).then(function(data){
                self.lead_per_model_count(data);
            });
        },
        lead_count_mediums:function(){
            $(".lead_count_header").html('Lead/oppty Count per Medium');
            $(".lead_count_footer").html('Lead/oppty Count per Medium This Year')
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_lead_per_model',
                args: ['utm.medium','medium_id'],
            }).then(function(data){
                self.lead_per_model_count(data);
            });
        },
        lead_count_sources:function(){
            $(".lead_count_header").html('Lead/oppty Count per Source');
            $(".lead_count_footer").html('Lead/oppty Count per Source This Year')
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_lead_per_model',
                args: ['utm.source','source_id'],
            }).then(function(data){
                self.lead_per_model_count(data);
            });
        },
        
        lead_per_model_count : function(lead_per_campaign){
            Highcharts.chart('lead-count-per-campaign-container', {
                chart: {
                    type: 'column',
                    marginBottom: 130
                },
                title: {
                    text: ''
                },
                xAxis: {
                    categories: lead_per_campaign.months,
                    title: {
                        text: 'Date'
                    },
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Average Count per Campaign'
                    },
                    stackLabels: {
                        enabled: true,
                        style: {
                            fontWeight: 'bold',
                            color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                        }
                    }
                },
                legend: {
                    align: 'left',
                    verticalAlign: 'bottom',
                    floating: true,
                    backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
                    borderColor: '#CCC',
                    borderWidth: 1,
                    shadow: false,
                },
                tooltip: {
                    headerFormat: '<b>{point.x}</b><br/>',
                    pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                },
                plotOptions: {
                    column: {
                        stacking: 'normal',
                        dataLabels: {
                            enabled: true,
                            color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                        }
                    }
                },
                series: lead_per_campaign.series
            });
        },
        roi_campaigns_graph:function(){
            $(".roi_title").html('Campaigns by ROI');
            $(".roi_footer").html('Campaigns by ROI This Year')
            var self = this;
            
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_model_by_roi',
                args: ['utm.campaign','campaign_id'],
            }).then(function(data){
                self.roi_graph('by-roi-container',data);
            });
        },
        roi_mediums_graph:function(){
            $(".roi_title").html('Mediums by ROI');
            $(".roi_footer").html('Mediums by ROI This Year')
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_model_by_roi',
                args: ['utm.medium','medium_id'],
            }).then(function(data){
                self.roi_graph('by-roi-container',data);
            });
        },
        roi_sources_graph:function(){
            $(".roi_title").html('Sources by ROI');
            $(".roi_footer").html('Sources by ROI This Year')
            var self = this;
            var crm_dashboard = this._rpc({
                model:'crm.dashboard',
                method: 'get_model_by_roi',
                args: ['utm.source','source_id'],
            }).then(function(data){
                self.roi_graph('by-roi-container',data);
            });
        },
        roi_graph:function(container_id,model_by_roi){
            Highcharts.chart(container_id, {
                chart: {
                    zoomType: 'xy'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: [{
                    categories: model_by_roi.models,
                    crosshair: true
                }],
                yAxis: [{ // Primary yAxis
                    labels: {
                        format: '',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    },
                    title: {
                        text: '',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    }
                }, { // Secondary yAxis
                    title: {
                        text: '',
                        style: {
                            color: Highcharts.getOptions().colors[0]
                        }
                    },
                    labels: {
                        format: '',
                        style: {
                            color: Highcharts.getOptions().colors[0]
                        }
                    },
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'top',
                    floating: true,
                    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
                },
                series: [{
                    name: 'ROI($)',
                    type: 'column',
                    yAxis: 1,
                    data: model_by_roi.roi_val,
                    tooltip: {
                        valueSuffix: ' $'
                    }
            
                }, {
                    name: 'ROI(%)',
                    type: 'spline',
                    data:  model_by_roi.roi_percent,
                    tooltip: {
                        valueSuffix: '%'
                    }
                }]
            });  
        },
        converted_lead:function(data){
            Highcharts.chart('converted-lead-container', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: data.months,
                },
                yAxis: {
                    title: {
                        text: 'Record Count'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: false
                    }
                },
                series: data.series,
            });
        },
        conversion_rate:function(data){
            Highcharts.chart('conversion-rate-container', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: data.months,
                },
                yAxis: {
                    title: {
                        text: 'Conversion Rate'
                    },
                    labels: {
                        format: '{value:.2f} %'
                    }
                },
                tooltip: {
                    valueDecimals: 2,
                    valueSuffix:'%'
                },
                
                series: data.series,
            });
        },
    });
    core.action_registry.add("dashboard_crm", dashboard_crm);
    return {
        dashboard_crm:dashboard_crm
    };
});