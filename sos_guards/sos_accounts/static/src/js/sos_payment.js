odoo.define('sos_accounts.payment', function (require) {
"use strict";

var SOSPayment = require('account.payment');

SOSPayment.ShowPaymentLineWidget.include({

	_onOpenPayment: function (event) {
        var invoiceId = parseInt($(event.target).attr('invoice-id'));
        var paymentId = parseInt($(event.target).attr('payment-id'));
        var moveId = parseInt($(event.target).attr('move-id'));
        var res_model;
        var id;
        if (moveId !== undefined && !isNaN(moveId)){
            res_model = "account.move";
            id = moveId;
        }
        else if (invoiceId !== undefined && !isNaN(invoiceId)){
            res_model = "account.invoice";
            id = invoiceId;
        } else if (paymentId !== undefined && !isNaN(paymentId)){
            res_model = "account.payment";
            id = paymentId;
        }
        //Open form view of account.move with id = move_id
        if (res_model && id) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: res_model,
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        }
    },

});

});
