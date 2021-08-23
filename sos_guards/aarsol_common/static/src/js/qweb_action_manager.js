odoo.define('aarsol_common.qweb_action_manager', function(require) {
    'use strict';

	var ajax = require('web.ajax');
	var ActionManager = require('web.ActionManager');
	var core = require('web.core');
	var crash_manager = require('web.crash_manager');
	var framework = require('web.framework');
	
	var session = require('web.session');
	var Dialog = require('web.Dialog');
	var rpc = require('web.rpc');
	
	var utils = require('report.utils');
	var ReportAction = require('report.client_action');
	
	var QWeb = core.qweb;
	
	var _t = core._t;
	var _lt = core._lt;
	
    var controller_url = null;
    var wkhtmltopdf_state;
    var action_model = null;
    var company_id = session.company_id;
    var print_copies = 1;
    var printer_type = 'zpl'

    var wkhtmltopdf_state;
    
    
// Messages that will be shown to the user (if needed).
var WKHTMLTOPDF_MESSAGES = {
    'install': _lt('Unable to find Wkhtmltopdf on this \nsystem. The report will be shown in html.<br><br><a href="http://wkhtmltopdf.org/" target="_blank">\nwkhtmltopdf.org</a>'),
    'workers': _lt('You need to start OpenERP with at least two \nworkers to print a pdf version of the reports.'),
    'upgrade': _lt('You should upgrade your version of\nWkhtmltopdf to at least 0.12.0 in order to get a correct display of headers and footers as well as\nsupport for table-breaking between pages.<br><br><a href="http://wkhtmltopdf.org/" \ntarget="_blank">wkhtmltopdf.org</a>'),
    'broken': _lt('Your installation of Wkhtmltopdf seems to be broken. The report will be shown in html.<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>')
};

var trigger_download = function (session, response, c, action, options) {
    return session.get_file({
        url: '/report/download',
        data: {data: JSON.stringify(response)},
        complete: framework.unblockUI,
        error: c.rpc_error.bind(c),
        success: function () {
            if (action && options && !action.dialog) {
                options.on_close();
            }
        },
    });
};

/**
 * This helper will generate an object containing the report's url (as value)
 * for every qweb-type we support (as key). It's convenient because we may want
 * to use another report's type at some point (for example, when `qweb-pdf` is
 * not available).
 */
var make_report_url = function (action) {
    var report_urls = {
        'qweb-html': '/report/html/' + action.report_name,
        'qweb-pdf': '/report/pdf/' + action.report_name,
        'qweb-xls': '/report/xls/' + action.report_name,
    };
    // We may have to build a query string with `action.data`. It's the place
    // were report's using a wizard to customize the output traditionally put
    // their options.
    if (_.isUndefined(action.data) || _.isNull(action.data) || (_.isObject(action.data) && _.isEmpty(action.data))) {
        if (action.context.active_ids) {
            var active_ids_path = '/' + action.context.active_ids.join(',');
            // Update the report's type - report's url mapping.
            report_urls = _.mapObject(report_urls, function (value, key) {
                return value += active_ids_path;
            });
        }
    } else {
        var serialized_options_path = '?options=' + encodeURIComponent(JSON.stringify(action.data));
        serialized_options_path += '&context=' + encodeURIComponent(JSON.stringify(action.context));
        // Update the report's type - report's url mapping.
        report_urls = _.mapObject(report_urls, function (value, key) {
            return value += serialized_options_path;
        });
    }
    return report_urls;
};

ActionManager.include({
    ir_actions_report: function (action, options) {
        var self = this;
        action = _.clone(action);

        var report_urls = make_report_url(action);
        
		if (action.xml_id == 'product.report_product_template_label' || action.xml_id == 'stock.action_report_location_barcode' || action.xml_id == 'product.report_product_label') {
			var txt_t;
			var person = null;
			$("#myModalpopup").remove();
			var model_popup = 
				'<div class="modal fade" id="myModalpopup" role="dialog">'+
				'<div class="modal-dialog modal-sm">'+
					'<div class="modal-content">'+
						'<div class="modal-header">'+
						  '<button type="button" class="close" data-dismiss="modal">&times;</button>'+
						  '<h4 class="modal-title">No Of Copies</h4>'+
						'</div>'+
						'<div class="modal-body">'+
						  '<input type="number" name="copies_count" value="1">'+
						'</div>'+
						'<div class="modal-footer">'+
						  '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
						  '<button type="button" class="btn btn-default pull-right copies_text_in" data-dismiss="modal">OK</button>'+
						'</div>'+
					  '</div>'+
					'</div>'+
				  '</div>'+
				'</div>';
			$('body').append(model_popup);
			if(action.context['no_of_prints'])
			    $("input[name='copies_count']").val(action.context['no_of_prints']);
			$("#myModalpopup").modal();
						                
			$('.copies_text_in').click(function() {
				var input_val = $("input[name='copies_count']").val()
				person = input_val;
				if (person == null || person == "") {
					txt_t = "Cancelled copies";
					return false;
				}
				else {
					if(parseInt(person)){
						print_copies = person;
						
						framework.blockUI();
						
					    var treated_actions = [];
					    var current_action = action;
					    do {
					    
					        report_urls = make_report_url(current_action);
					        							        
					        controller_url = report_urls['qweb-pdf'];
					        action_model = action.model;
					        startConnection();
					        							                               
					        treated_actions.push(current_action);
					        current_action = current_action.next_report_to_generate;
					    
					    } while (current_action && !_.contains(treated_actions, current_action));
					    //Second part of the condition for security reasons (avoids infinite loop possibilty).
						
						framework.unblockUI();
						
					    return;

							
						
						
						            				
					}else {
						return false;
					}
			   }
		   });
		   
		   
		    
                            
                            

		} else if (action.report_type === 'qweb-html') {
            var client_action_options = _.extend({}, options, {
                report_url: report_urls['qweb-html'],
                report_name: action.report_name,
                report_file: action.report_file,
                data: action.data,
                context: action.context,
                name: action.name,
                display_name: action.display_name,
            });
            return this.do_action('report.client_action', client_action_options);
        } else if (action.report_type === 'qweb-pdf') {
            framework.blockUI();
            // Before doing anything, we check the state of wkhtmltopdf on the server.
            (wkhtmltopdf_state = wkhtmltopdf_state || this._rpc({route: '/report/check_wkhtmltopdf'})).then(function (state) {
                // Display a notification to the user according to wkhtmltopdf's state.
                if (WKHTMLTOPDF_MESSAGES[state]) {
                    self.do_notify(_t('Report'), WKHTMLTOPDF_MESSAGES[state], true);
                }

                if (state === 'upgrade' || state === 'ok') {
                    // Trigger the download of the PDF report.
                    var response;
                    var c = crash_manager;

                    var treated_actions = [];
                    var current_action = action;
                    do {
                        report_urls = make_report_url(current_action);
                        response = [
                            report_urls['qweb-pdf'],
                            action.report_type, //The 'root' report is considered the maine one, so we use its type for all the others.
                        ];
                        
		                if (action.xml_id == 'dokkan_ext.report_order_label') {
                             
                            print_copies = 1;            
                            
                            controller_url = report_urls['qweb-pdf'];
                            action_model = action.model;
                            //return startConnection();
                            startConnection();
                            framework.unblockUI(); 
                       
		                   
                        } else {
                            var success = trigger_download(self.getSession(), response, c, current_action, options);
                            if (!success) {
                                self.do_warn(_t('Warning'), _t('A popup window with your report was blocked.  You may need to change your browser settings to allow popup windows for this page.'), true);
                            }
                        }
                        treated_actions.push(current_action);
                        current_action = current_action.next_report_to_generate;
                    } while (current_action && !_.contains(treated_actions, current_action));
                    //Second part of the condition for security reasons (avoids infinite loop possibilty).

                    return;

                } else {
                    // Open the report in the client action if generating the PDF is not possible.
                    var client_action_options = _.extend({}, options, {
                        report_url: report_urls['qweb-html'],
                        report_name: action.report_name,
                        report_file: action.report_file,
                        data: action.data,
                        context: action.context,
                        name: action.name,
                        display_name: action.display_name,
                    });
                    framework.unblockUI();
                    return self.do_action('report.client_action', client_action_options);
                }
            });
        } else if (action.report_type === 'qweb-xls' || action.report_type === 'qweb-ppt' || action.report_type === 'qweb-pptp' || action.report_type === 'qweb-lbl') {
            framework.blockUI();               
                
            // Trigger the download of the PDF report.
            var response;
            var c = crash_manager;

            var treated_actions = [];
            var current_action = action;
            do {
                report_urls = make_report_url(current_action);
                response = [
                    report_urls['qweb-pdf'],
                    action.report_type, //The 'root' report is considered the maine one, so we use its type for all the others.
                ];
                var success = trigger_download(self.getSession(), response, c, current_action, options);
                if (!success) {
                    self.do_warn(_t('Warning'), _t('A popup window with your report was blocked.  You may need to change your browser settings to allow popup windows for this page.'), true);
                }

                treated_actions.push(current_action);
                current_action = current_action.next_report_to_generate;
            } while (current_action && !_.contains(treated_actions, current_action));
            //Second part of the condition for security reasons (avoids infinite loop possibilty).

            return;
                
            
        } else {
            self.do_warn(_t('Error'), _t('Non qweb reports are not anymore supported.'), true);
            return;
        }
    }
});


ReportAction.include({
	start: function () {
        var self = this;
        this.set('title', this.title);
        this.iframe = this.$('iframe')[0];
        return $.when(this._super.apply(this, arguments), session.is_bound).then(function () {
            var web_base_url = session['web.base.url'];
            var trusted_host = utils.get_host_from_url(web_base_url);
            var trusted_protocol = utils.get_protocol_from_url(web_base_url);
            self.trusted_origin = utils.build_origin(trusted_protocol, trusted_host);

            self.$buttons = $(QWeb.render('report.client_action.ControlButtons', {}));
            self.$buttons.on('click', '.o_report_edit', self.on_click_edit);
            self.$buttons.on('click', '.o_report_print', self.on_click_print);
            self.$buttons.on('click', '.o_report_excel', self.on_click_excel);
            self.$buttons.on('click', '.o_report_save', self.on_click_save);
            self.$buttons.on('click', '.o_report_discard', self.on_click_discard);

            self._update_control_panel();

            // Load the report in the iframe. Note that we use a relative URL.
            self.iframe.src = self.report_url;

            // Once the iframe is loaded, check if we can edit the report.
            self.iframe.onload = function () {
                self._on_iframe_loaded();
            };
        });
    },
    
    on_click_excel: function () {
        debugger;
        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-xls',
            'report_name': this.report_name,
            'report_file': this.report_file,
            'data': this.data,
            'context': this.context,
            'display_name': this.title,
        };
        return this.do_action(action);
    },

});   

	var qzVersion = 0;


    function findVersion() {
        qz.api.getVersion().then(function(data) {
            qzVersion = data;
            console.log("Version of QZ Tray: " + data);
        });
    }

    function startConnection(config) {
        qz.security.setCertificatePromise(function(resolve, reject) {
            $.ajax("/label_zebra_printer/static/src/lib/digital-certificate.txt").then(resolve, reject);
        });
        var privateKey = "-----BEGIN RSA PRIVATE KEY-----\n" +
            "MIIEpQIBAAKCAQEAwRc05UhbsKtU/SupjO8HHrVKKwglsfJeBoUMQoHo41a440Do\n" +
            "r6dbVI/HJITAQ1swIJjwmD9QqSVesnHnc7e6zlkj1ff1fDsOomIzX2SnB2CA9eiw\n" +
            "5cfsXth6grZ6NIr7fc9NzyDpl3XcCEE+2ijbZCB0hWIVRkFBYh+RJPnoEFtb8njM\n" +
            "J9V/YgXQf969jIFjAS8QVsDBvnnSsTeoE/2AXs1tRO4bzPEF65UouVeKJfBcICK4\n" +
            "T7ZMObJEKAHc/PMLd9pLBG9Gg4/59AoeWuM92qti1i3307WFGKKGNNZ5Tt/EeX+2\n" +
            "5LPu8yilRK+F3hlpvvTNzwK7KAvoNWBCQll2rQIDAQABAoIBACyBrt2Smh/UvhhE\n" +
            "8iXcCqYXX2sfy6CCnw2dqT/DNe0A1kj7cybZyoFpSpuuRarA4A0Dc6GEJpF2Xad/\n" +
            "/bt8hACAJ3RwXRMvgaYIQJMiXiWjJtaHtg6g0GjkOQjcCrsFtgY/vE2b5nvU3MzC\n" +
            "TTx34mnn2TPNcd3puKpnYEtHlyf9oBEKOE85gyOv1fMUZeQw/kPSNEr+gWQnj/u6\n" +
            "rchlzPhHZjmMuB5At6/yWURnjbFuYwgb2djjDNY52KEcCGJvDsrrFqs5EKE40u96\n" +
            "CNNtQNAye5mT89Jl2JwPJobpsycDEqZEayc6kJX/77e/2Y3JIuY9gm+Q17opHkYg\n" +
            "7IbQP7kCgYEA8ZC48g01YaCTk2DoRIXF0hRb8MbjeVs5ej20l7GbicWuF3u4LNld\n" +
            "vQgFhC2xiIFl39HwoRGHdN/NYo5TZcGsnScsItM4gIlZCruIpaj9wWiKbDwWf2p7\n" +
            "V8+H8KrSsqaX1Jy2mieG/kgdXI4bqPCh74sEjw1g6XTboYBFsrH1s18CgYEAzKD0\n" +
            "33f42BVie/p8ta+tqXNOsr4U/2czZU8ZSievheZcMyoQLmsJcIiOO4eZ55h5MR7d\n" +
            "bL6XaIfXrpuaLANkx2wi5PEOtp5fIT4u+AJb6DQdcRfYZ3VMkG00b2hSCSUbrWho\n" +
            "9x9wQaGC1RKj+XBAUgydXQFdXZi8sOApmTpr/XMCgYEAhfJt2yof04aqzioKIRTc\n" +
            "YGURpi1irUQ8VuAoZ4UAbiDDLBpaQeQ16j+sb2K28q5twvIyr918cv42cNPiwqXm\n" +
            "BS5XdugQiJWgXicm2lUegERrnSCkiPqOcl6NTpIqSw29WxOa3VfVruJmBZB3HfJw\n" +
            "mNdJK9mLR2iY8LCj9TZgu5kCgYEApwBdmNui3UdmnuQpT2ZXBsoyWjJDlMW27mGF\n" +
            "tD17RH5ilOcpWZjFlW/9FJxwgNCxZ+NWtt89VnQ3FCutwWnrn82jFNGfPm82GD1V\n" +
            "u9bBB1sxBBF/7b+Pgvd9Kccr3IbKddWWhMjFpuqXiimyZWq1M8FT1Im+lxqGNJxd\n" +
            "ls5VP/0CgYEA5S/gZ1gPGgUE18R4cMNDstTA90QFC15yzkRpLtth9DPoKoX/r2G0\n" +
            "8eKN9tIBY+VBEf00g6stSN02ncq5LKE/tS1OO4OmM+u6G/qjPAoW2AlPMqnptyFo\n" +
            "kFEGUC6AlTfS2E5WfF38SdwsBi6c2QIFBP2GKAjo5pC9WglhnVvVPBE=\n" +
            "-----END RSA PRIVATE KEY-----\n";

        qz.security.setSignaturePromise(function(toSign) {
            return function(resolve, reject) {
                try {
                    var pk = new RSAKey();
                    pk.readPrivateKeyFromPEMString(strip(privateKey));
                    var hex = pk.signString(toSign, 'sha1');
                    //console.log("DEBUG: \n\n" + stob64(hextorstr(hex)));
                    resolve(stob64(hextorstr(hex)));
                } catch (err) {
                    console.error(err);
                    reject(err);
                }
            };
        });

        function strip(key) {
            if (key.indexOf('-----') !== -1) {
                return key.split('-----')[2].replace(/\r?\n|\r/g, '');
            }
        }

        if (!qz.websocket.isActive()) {
            console.log('Waiting default');
            qz.websocket.connect(config).then(function() {
                console.log('Active success');
                findVersion();
                findPrinters();
            });
        } else {
            console.log('An active connection with QZ already exists.', 'alert-warning');
        }
    }

    function findPrinters() {
            if (action_model == 'stock.picking')
            {
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    printer_type = company[0].printer_type
                    qz.printers.find(company[0].shipping_printer).then(function(data) {
                         console.log("Found: " + data);
                         setPrinter(data);
                     }).catch(function(err) {
                     console.log("Found Printer Error:", err);
                    });
                });
            }
            else if (action_model == 'stock.location')
            {
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    printer_type = company[0].printer_type
                    qz.printers.find(company[0].location_printer).then(function(data) {
                         console.log("Found: " + data);
                         setPrinter(data);
                     }).catch(function(err) {
                     console.log("Found Printer Error:", err);
                    });
                });
            }
            else
            {
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    printer_type = company[0].printer_type
                    qz.printers.find(company[0].product_printer).then(function(data) {
                         console.log("Found: " + data);                         
                         setPrinter(data);
                     }).catch(function(err) {
                     console.log("Found Printer Error:", err);
                    });
                });
            }
       }

    function setPrinter(printer) {        
		var cf = getUpdatedConfig();
        cf.setPrinter(printer);
        if (typeof printer === 'object' && printer.name == undefined) {
            var shown;
            if (printer.file != undefined) {
                shown = "<em>FILE:</em> " + printer.file;
            }
            if (printer.host != undefined) {
                shown = "<em>HOST:</em> " + printer.host + ":" + printer.port;
            }
        } else {
            if (printer.name != undefined) {
                printer = printer.name;
            }

            if (printer == undefined) {
                printer = 'NONE';
            }
            if (action_model == 'stock.picking') {
                print_picking_label();
            }
            else if (action_model == 'sale.order') {
                print_picking_label();
            }
            else if (action_model == 'stock.location'){
                print_location_label();
            }
            else if (action_model == 'product.template'){
                print_product_label();
            }
            else if (action_model == 'product.product'){
                print_variant_label();
            }
        }
    }
    /// QZ Config ///
    var cfg = null;

    function getUpdatedConfig() {
        if (cfg == null) {
            cfg = qz.configs.create(null);
        }

        cfg.reconfigure({
            copies: print_copies,
        });
        return cfg
    }
    
    function print_variant_label() {
        console.log("cccccccccccccccc", controller_url)
        debugger;
        ajax.jsonRpc("/zebra" + controller_url, 'call', {})
            .then(function(res_data) {
                console.log("result", res_data);
                var config = getUpdatedConfig();
                var width = 2.0;
                var height = 1.0;
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    height = company[0].product_height
                    width = company[0].product_width
                });
                config.reconfigure({
                    size: {'width': width, 'height': height},
                });

                res_data.data.forEach(function(product) {
                    if (printer_type == 'zpl'){
                        
						var printData =
                            [
                                '^XA',
								'^FO80,20^ADN,18,10^FDwww.dokkanafkar.com^FS',
								'^FO25,45^BY2^BCN,50,Y^FD'+product.barcode+'^FS',
								'^FO5,140^ADN,18,10^FD'+product.name+'^FS',
								'^FO5,165^GB195,30,2^FS',
								'^FO125,165^GB0,30,2^FS',
								'^FO200,165^GB200,30,2,,0^FS',
								'^FO10,170^ADN,18,10^FDSAR '+product.price+'^FS',
								'^FO135,170^ADN,18,10^FDC4-W5^FS',
								'^FO210,170^ADN,18,10^FD'+product.variants+'^FS',
								'^XZ',							
                            ];
                    }
                    else{
                        var printData =
                            [
                                '\nN\n',
                                'q609\n',
                                'Q203,26\n',
                                'D7\n',
                                'A190,10,0,3,1,1,N,"'+product.name+'"\n',
                                'B190,60,0,1,1,2,60,B,"'+product.barcode+'"\n',
                                '\nP1,1\n'
                            ];
                    }
                    console.log("ddddddddddddd", printData)
                    qz.print(config, printData).catch(function(e) { console.error(e); });
                    });

            }).done(function() {
                location.reload();
                console.log("Printing done Variant Label");
            });
    }

    function print_product_label() {
        console.log("cccccccccccccccc", controller_url)
       
        ajax.jsonRpc("/zebra" + controller_url, 'call', {})
            .then(function(res_data) {
                console.log("result", res_data);
                var config = getUpdatedConfig();
                var width = 2.00;
                var height = 1.00;
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    height = company[0].product_height
                    width = company[0].product_width
                });
                config.reconfigure({
                    size: {'width': width, 'height': height},
                });

                res_data.data.forEach(function(product) {
                    if (printer_type == 'zpl'){
                        
						var printData =
                            [
                                '^XA',
								'^FO80,20^ADN,18,10^FDwww.dokkanafkar.com^FS',
								'^FO25,45^BY2^BCN,50,Y^FD'+product.barcode+'^FS',
								'^FO5,140^ADN,18,10^FD'+product.name+'^FS',
								'^FO5,165^GB195,30,2^FS',
								'^FO125,165^GB0,30,2^FS',
								'^FO200,165^GB200,30,2,,0^FS',
								'^FO10,170^ADN,18,10^FDSAR '+product.price+'^FS',
								'^FO135,170^ADN,18,10^FDC4-W5^FS',								
								'^XZ',							
                            ];
                    }
                    else{
                        var printData =
                            [
                                '\nN\n',
                                'q609\n',
                                'Q203,26\n',
                                'D7\n',
                                'A190,10,0,3,1,1,N,"'+product.name+'"\n',
                                'B190,60,0,1,1,2,60,B,"'+product.barcode+'"\n',
                                '\nP1,1\n'
                            ];
                    }
                    console.log("ddddddddddddd", printData)
                    qz.print(config, printData).catch(function(e) { console.error(e); });
                    });

            }).done(function() {
                location.reload();
                console.log("Printing done Product Label");
            });
    }

    function print_picking_label() {
        ajax.jsonRpc("/zebra" + controller_url, 'call', {})
            .then(function(res_data) {
                var config = getUpdatedConfig();
                var width = 1.25;
                var height = 1;
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    height = company[0].shipping_height
                    width = company[0].shipping_width
                });
                config.reconfigure({
                    size: {'width': width, 'height': height},
                });
                res_data.data.forEach(function(picking) {
                    if (printer_type == 'zpl'){
                        var printData =
                            [
                                '^XA',
                                '^FO20,25^BY2,20,50^BCN,50,Y^FD'+picking.label+'^FS',                                
                                '^FO5,110^ADN,18,10^FD'+picking.ordername+' ('+picking.items+' Items)^FS',                                
                                '^FO5,145^GB400,30,2^FS',
								'^FO200,145^GB0,30,2^FS',
								'^FO10,150^ADN,18,10^FD'+picking.shipper+'^FS',
								'^FO210,150^ADN,18,10^FD'+picking.picker+'^FS',
                                '^XZ',
                            ];
                    }
                    else{
                        var printData =
                            [
                                '\nN\n',
                                'q609\n',
                                'Q203,26\n',
                                'B190,10,0,1,1,2,60,B,"'+product.label+'"\n',
                                '\nP1,1\n'
                            ];
                    }
                    console.log("ddddddddddddd", printData)
                    qz.print(config, printData).catch(function(e) { console.error(e); });
                });

            }).done(function() {
                //location.reload();
                console.log("Printing done Picking Label");
            });
    }
    function print_location_label() {
        ajax.jsonRpc("/zebra" + controller_url, 'call', {})
            .then(function(res_data) {
                console.log("result", res_data);
                var config = getUpdatedConfig();
                var width = 1.25;
                var height = 1;
                rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }).done(function(company) {
                    height = company[0].location_height
                    width = company[0].location_width
                });
                config.reconfigure({
                    size: {'width': width, 'height': height},
                });
                res_data.data.forEach(function(location) {
                    if (printer_type == 'zpl'){
                        var printData =
                            [
                                '^XA',
                                '^CF0,130',
                                '^FO100,120^FD'+location.name+'^FS',
                                '^BY2,20,120',
                                '^FO250,250^BC^FD'+location.barcode+'^FS',
                                '^XZ',
                            ];
                    }
                    else{
                        var printData =
                            [
                                '\nN\n',
                                'q609\n',
                                'Q203,26\n',
                                'D7\n',
                                'A190,10,0,3,1,1,N,"'+location.name+'"\n',
                                'B190,60,0,1,1,2,60,B,"'+location.barcode+'"\n',
                                '\nP1,1\n'
                            ];
                    }
                    console.log("ddddddddddddd", printData)
                    qz.print(config, printData).catch(function(e) { console.error(e); });
                    });

            }).done(function() {
                location.reload();
                console.log("Printing done Location Label");
            });
    }
    
});
