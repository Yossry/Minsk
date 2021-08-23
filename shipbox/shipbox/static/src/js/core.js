odoo.define('shipbox.core', function (require) {
"use strict";

var core = require('web.core')

/*
This is the function that the Linea Pro iOS cases use to pass in
Barcode data to a webapp.
 */
window.BarcodeData = function(barcode, type, typeText) {
    core.bus.trigger('barcode_scanned', barcode, document);
};



var ajax = require('web.ajax');
var Widget = require('web.Widget');
var SystrayMenu = require('web.SystrayMenu');
var print_queue = require('shipbox.print_queue');
var PrintQueueContainer = print_queue.PrintQueueContainer;

var ShipboxCoreWidget = Widget.extend({
    template: 'ShipboxCoreWidget',
    endpoint_url: false,
    endpoint_name: '',
    start: function() {
        var self = this;
        this._rpc({
            model: 'shipbox.endpoint',
            method: 'get_endpoint',
        }).then(function (result) {
            console.log(result);
            self.endpoint_url = result.url;
            self.endpoint_name = result.name;
            self._scaleStart();
            self._printStart();
        });
        return this._super();
    },

    /*
        Internal Logging Events
     */
    events: [],
    add_event: function (event) {
        this.events.push(event);
        if (this.events.length > 20) {
            this.events = this.events.slice(10);
            var html = '';
            _.each(this.events, function(event) {
                html = '<li>' + event.type + ': ' + event.msg + '</li>' + html;
            });
            this.$('.dropdown-menu').html(html);
        } else {
            var e = '<li>' + event.type + ': ' + event.msg + '</li>';
            this.$('.dropdown-menu').prepend(e);
        }
    },
    get_event: function(type, msg) {
        return {'type': type, 'msg': msg};
    },
    get_scale_event: function(msg) {
        return this.get_event('Scale', msg);
    },
    get_print_event: function(msg) {
        return this.get_event('Print', msg);
    },

    /*
        Scale portion of Shipbox
     */
    scale_reading: 0.0,
    scale_started: false,
    scale_timer: false,
    scale_connection_errors_count: 0,
    scale_speed: 1000,
    scale_max: 0.0,
    _scaleStart: function () {
        var event = this.get_scale_event();
        this.scale_reading = 0.0;
        this.scale_connection_errors_count = 0;
        this.scale_speed = 1000;
        this.scale_max = 0.0;
        if (this.endpoint_url) {
            event.msg = 'Start';
            this.scale_read_from_scale();
        } else {
            event.msg = 'No Shipbox Endpoint';
        }
        this.add_event(event);
    },
    scale_read_from_scale: function() {
        if (this.scale_connection_errors_count < 100) {
            var url = this.endpoint_url + '/hw_proxy/scale_read/';
            ajax.jsonRpc(url, null, {}, {'shadow': true})
                .done(this.scale_response_from_scale.bind(this))
                .fail(this.error_from_scale.bind(this))
                .always(this.setup_read_timer.bind(this));
        }
    },
    scale_response_from_scale: function(result) {
        var w = result.weight.toFixed(3);
        if (result.weight > this.scale_max) {
            this.add_event(this.get_scale_event('New Max Weight: ' + w));
            this.scale_max = result.weight;
        }
        this.scale_reading = parseFloat(w);
        this.scale_speed = 1000;
        $('.shipbox_scale_reading_auto').text(w);
    },
    error_from_scale: function(error, ev) {
        ev.preventDefault();
        ev.stopImmediatePropagation();
        var event = this.get_scale_event();
        this.scale_connection_errors_count += 1;
        this.scale_speed = 1000;
        if (this.scale_connection_errors_count > 3) {
            event.msg = this.scale_connection_errors_count + ' Errors. Throttling...';
            this.scale_speed = 10000;
        } else if (this.scale_connection_errors_count > 6) {
            event.msg = this.scale_connection_errors_count + ' Errors. Throttling more...';
            this.scale_speed = 30000;
        }
        if (event.msg) {
            this.add_event(event);
        }
    },
    setup_read_timer: function() {
        this.scale_timer = setTimeout(this.scale_read_from_scale.bind(this), this.scale_speed);
    },
    get_scale_reading: function() {
        return this.scale_reading;
    },
    /*
        Print parts.
     */
    _printStart: function() {
        PrintQueueContainer.setMainQueue(this.endpoint_url, this.print_callback.bind(this));
    },
    print_callback: function(msg) {
        this.add_event(this.get_print_event(msg));
    },
});

SystrayMenu.Items.push(ShipboxCoreWidget);

return {
    ShipboxCoreWidget: ShipboxCoreWidget,
};

});