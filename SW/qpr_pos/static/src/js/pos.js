odoo.define('qpr_pos.qpr_pos', function(require) {
    "use strict";

    var core = require('web.core');
    var models = require('point_of_sale.models');

    var _t = core._t;

    models.load_fields('product.product', 'name_arabic');

    // models.load_models([{
    //     model: 'res.bank',
    //     fields: ['name'],
    //     loaded: function(self, banks) {
    //         self.banks = banks;
    //     },
    // }]);

    // var CheckDetailPopupWidget = PopupWidget.extend({
    //     template: 'CheckDetailPopupWidget',
    //     init: function() {
    //         this._super.apply(this, arguments);
    //         this.banks = this.pos.banks;
    //     },
    //     show: function(options) {
    //         options = options || {};
    //         this.bank_id = options.line && options.line.bank_id || '';
    //         this.due_date = options.line && options.line.due_date || '';
    //         this.check_number = options.line && options.line.check_number || '';
    //         this._super(options);
    //         this.renderElement();
    //         this.chrome.screens.payment.unlock_payment_screen();
    //     }
    // });
    // gui.define_popup({
    //     name: 'check_details',
    //     widget: CheckDetailPopupWidget
    // });

    // screens.PaymentScreenWidget.include({

    //     unlock_payment_screen: function() {
    //         $('body').off('keypress', this.keyboard_handler);
    //         $('body').off('keydown', this.keyboard_keydown_handler);
    //     },

    //     lock_payment_screen: function() {
    //         $('body').on('keypress', this.keyboard_handler);
    //         $('body').on('keydown', this.keyboard_keydown_handler);
    //     },

    //     render_paymentlines: function() {
    //         self = this;
    //         this._super.apply(this, arguments);
    //         var order = this.pos.get_order();
    //         this.$('.check-details').on('click', function() {
    //             if (!order.get_client()) {
    //                 self.gui.show_popup('confirm',{
    //                     title: _t('Select Customer!'),
    //                     body:  _t('Please select customer in order to enter the check details.'),
    //                     confirm: function() {
    //                         self.gui.show_screen('clientlist');
    //                     },
    //                 });
    //             } else {
    //                 self.open_check_detail_dialog($(this).data('cid'));
    //             }
    //         });
    //     },
    //     order_is_valid: function(force_validation) {
    //         var lines = this.pos.get_order().get_paymentlines();
    //         var error = false;
    //         for (var i = 0; i < lines.length; i++) {
    //             if (!lines[i].is_detail_filled() && lines[i].is_detail_required()) {
    //                 error = true;
    //             }
    //         }
    //         if (error) {
    //             this.gui.show_popup('error', {
    //                 'title': _t('Bank Detail Missing'),
    //                 'body': _t('bank details must be fill in order to validate the order'),
    //             });
    //             return false;
    //         }
    //         return this._super.apply(this, arguments);
    //     },
    //     open_check_detail_dialog: function(cid) {
    //         var self = this;
    //         var order = this.pos.get_order();
    //         var paymentline = _.findWhere(order.get_paymentlines(), {
    //             'cid': cid
    //         });
    //         this.pos.gui.show_popup('check_details', {
    //             'title': _t('Check Details For ' + paymentline.name),
    //             'line': paymentline,
    //             confirm: function() {
    //                 var bank_id = this.$('select[name="bank_id"]').val();
    //                 var due_date = this.$('input[name="due_date"]').val();
    //                 var check_number = this.$('input[name="check_number"]').val();
    //                 if (bank_id)
    //                     paymentline.set_bank_name(bank_id);
    //                 if (due_date)
    //                     paymentline.set_due_date(due_date);
    //                 if (check_number)
    //                     paymentline.set_check_number(check_number);

    //                 if (paymentline.is_detail_filled()) {
    //                     self.lock_payment_screen();
    //                     this.gui.close_popup();
    //                 }
    //             },
    //             cancel: function() {
    //                 self.lock_payment_screen();
    //                 this.gui.close_popup();
    //             }

    //         });
    //     }

    // });

    // var _super_paymentline = models.Paymentline;
    // models.Paymentline = models.Paymentline.extend({
    //     initialize: function(attributes, options) {
    //         _super_paymentline.prototype.initialize.apply(this, arguments);
    //     },
    //     set_bank_name: function(value) {
    //         this.bank_id = parseInt(value);
    //     },
    //     set_due_date: function(value) {
    //         this.due_date = value;
    //     },
    //     set_check_number: function(value) {
    //         this.check_number = value;
    //     },
    //     is_detail_required: function() {
    //         return this.cashregister.journal.check_details;
    //     },
    //     is_detail_filled: function() {
    //         if (this.bank_id && this.due_date && this.check_number) {
    //             return true;
    //         }
    //         return false;
    //     },
    //     export_as_JSON: function() {
    //         var res = _super_paymentline.prototype.export_as_JSON.apply(this, arguments);
    //         res.bank_id = this.bank_id;
    //         res.due_date = this.due_date;
    //         res.check_number = this.check_number;
    //         return res
    //     },
    //     init_from_JSON: function(json) {
    //         _super_paymentline.prototype.init_from_JSON.apply(this, arguments);
    //         this.bank_id = json.bank_id;
    //         this.due_date = json.due_date;
    //         this.check_number = json.check_number;
    //     }

    // });




});