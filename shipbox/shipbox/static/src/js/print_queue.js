odoo.define('shipbox.print_queue', function (require) {
"use strict";

var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');

ActionManager.include({
    _executeCloseAction: function (action, options) {
        if (action.shipbox_print) {
            console.log(action.shipbox_print);
            console.log(PrintQueueContainer.getMainQueue());
            if (action.shipbox_print.endpoint_url) {
                PrintQueueContainer.getQueue(action.shipbox_print.endpoint_url).print(action.shipbox_print)
            } else if (PrintQueueContainer.getMainQueue()) {
                PrintQueueContainer.getMainQueue().print(action.shipbox_print);
            }
        }
        if (action.shipbox_serial_file) {
            console.log(action.shipbox_serial_file);
            SerialFileUpload.send_file(action.shipbox_serial_file);
        }
        return this._super(action, options);
    }
});

// helper
var blobToBase64 = function(blob, callback) {
    var reader = new FileReader();
    reader.onload = function() {
        var dataUrl = reader.result;
        var base64 = dataUrl.split(',')[1];
        callback(base64);
    };
    reader.readAsDataURL(blob);
};

var SerialFileUpload = {
    send_file: function (payload) {
        var url = payload.endpoint_url + '/hw_proxy/serial_file';
        ajax.jsonRpc(url, null, payload, {'shadow': true})
            .done(function(e){console.log('send_file done'); console.log(e);})
            .fail(function(e){console.log('send_file fail'); console.log(e);})
    }
}

var PrintQueueContainer = {
    queues: {},
    main_queue: false,
    event_callback: false,
    setMainQueue: function(endpoint_url, callback) {
        if (callback) {
            this.event_callback = callback;
        }
        var new_runner = new PrinterRunner();
        new_runner.endpoint_url = endpoint_url;
        new_runner.event_callback = this.event_callback;
        new_runner.start();
        this.queues[endpoint_url] = new_runner;
        this.main_queue = new_runner;
    },
    getMainQueue: function() {
        return this.main_queue;
    },
    getQueue: function(endpoint_url) {
        if (!this.queues[endpoint_url]) {
            var new_runner = new PrinterRunner();
            new_runner.endpoint_url = endpoint_url;
            new_runner.event_callback = this.event_callback;
            new_runner.start();
            this.queues[endpoint_url] = new_runner;
            return new_runner;
        } else {
            return this.queues[endpoint_url];
        }
    }
}

var PrinterRunner = function(){
    this.endpoint_url = false;
    this.started = false;
    this._can_print_label = false;
    this._backlog = [];
    this.connection_errors_count = 0;
    this.start_wait_count = 0
    this.event_callback = false;

    this.can_print_label = function () {
        if (!this.started) {
            this.start();
            return false;
        }
        return this._can_print_label;
    }

    this.start = function () {
        this.started = true;
        if (!this.endpoint_url && this.start_wait_count < 10) {
            this.start_wait_count += 1;
            setTimeout(this.start.bind(this), 500);
        } else if (this.endpoint_url) {
            var url = this.endpoint_url + '/hw_proxy/status_json';
            ajax.jsonRpc(url, null, {}, {'shadow': true})
                .done(this.response_status.bind(this))
                .fail(this.error_response_status.bind(this))
        }
    }

    this.response_status = function (response) {
        if (response && response.print_queue.status == 'connected') {
            if (this.event_callback) {
                this.event_callback('Connected to ' + this.endpoint_url);
            }
            this._can_print_label = true;
            if (this._backlog.length) {
                for (var i = 0; i < this._backlog.length; i++) {
                    this.print(this._backlog[i]);
                }
                this._backlog = [];
            }
        } else {
            this._can_print_label = false;
            this.start();
        }
    }

    this.error_response_status = function (response, ev) {
        ev.preventDefault();
        ev.stopImmediatePropagation();
        console.log(response);
        if (this.event_callback) {
            this.event_callback('Error connecting to ' + this.endpoint_url);
        }
        this.connection_errors_count += 1;
    }

    this.print = function (attachment) {
        if (this.event_callback) {
            this.event_callback('Queuing ' + attachment.name);
        }
        if (this._can_print_label) {
            if (!attachment.data) {
                this.download_and_print(attachment);
                return;
            }
            var url = this.endpoint_url + '/hw_proxy/print_queue';
            ajax.jsonRpc(url, null, {'attachment': attachment}, {'shadow': true})
                .done(this.print_response.bind(this))
                .fail(this.error_response_status.bind(this))
        } else {
            this._backlog.push(attachment);
        }
    }

    this.print_message = function (message) {
        var self = this;
        if (message._attachmentIDs.length && this.can_print_label()) {
            for (var i = 0; i < message._attachmentIDs.length; i++) {
                var attachment = message._attachmentIDs[i];
                if (attachment.filename.indexOf('Label') >= 0) {
                    this.download_and_print(attachment);
                }
            }
        }
    }

    this.download_and_print = function (attachment) {
        var self = this;
        var req = new XMLHttpRequest();
        req.open("GET", attachment.url, true);
        req.responseType = "blob";
        req.onload = function (event) {
            var blob = req.response;
            blobToBase64(blob, function(b64data) {
                attachment.data = b64data;
                self.print(attachment);
            });
        };

        req.send();
    }

    this.print_response = function(response) {
        if (this.event_callback) {
            this.event_callback('Print success.');
        }
    }

    return this;
};

return {
    PrintQueueContainer: PrintQueueContainer,
    PrinterRunner: PrinterRunner,
};
});