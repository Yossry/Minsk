/*
    @Author: KSOLVES India Private Limited
    @Email: sales@ksolves.com
*/

odoo.define('ks_pos_low_stock_alert.ks_low_stock', function (require) {
    "use strict";

    var ks_models = require('point_of_sale.models');
    var ks_screens = require('point_of_sale.screens');
    var ks_utils = require('ks_pos_low_stock_alert.utils');

    ks_models.load_fields('product.product', ['type', 'qty_available']);
    var ks_super_pos = ks_models.PosModel.prototype;

    ks_models.PosModel = ks_models.PosModel.extend({
        initialize: function (session, attributes) {
            this.ks_load_product_quantity_after_product();
            ks_super_pos.initialize.call(this, session, attributes);
        },

        ks_get_model_reference: function (ks_model_name) {
            var ks_model_index = this.models.map(function (e) {
                return e.model;
            }).indexOf(ks_model_name);
            if (ks_model_index > -1) {
                return this.models[ks_model_index];
            }
            return false;
        },

        ks_load_product_quantity_after_product: function () {
            var ks_product_model = this.ks_get_model_reference('product.product');
            var ks_product_super_loaded = ks_product_model.loaded;
            ks_product_model.loaded = (self, ks_products) => {
                var done = $.Deferred();
                if(!self.config.allow_order_when_product_out_of_stock){
                    var ks_blocked_product_ids = [];
                    for(var i = 0; i < ks_products.length; i++){
                        if(ks_products[i].qty_available <= 0 && ks_products[i].type == 'product'){
                            ks_blocked_product_ids.push(ks_products[i].id);
                        }
                    }
                    var ks_blocked_products = ks_products.filter(function(p, index, arr) {
                        return ks_blocked_product_ids.includes(p.id);
                    });
                    ks_products = ks_products.concat(ks_blocked_products);
                }

                ks_product_super_loaded(self, ks_products);
                self.ks_update_qty_by_product_id(self, ks_products);
                done.resolve();
            }
        },

        ks_update_qty_by_product_id(self, ks_products){
            if(!self.db.qty_by_product_id){
                self.db.qty_by_product_id = {};
            }
            ks_products.forEach(ks_product => {
                self.db.qty_by_product_id[ks_product.id] = ks_product.qty_available;
            });
            self.ks_update_qty_on_product();
        },

        ks_update_qty_on_product: function () {
            var self = this;
            var ks_products = self.db.product_by_id;
            var ks_product_quants = self.db.qty_by_product_id;
            for(var pro_id in self.db.qty_by_product_id){
                ks_products[pro_id].qty_available = ks_product_quants[pro_id];
            }
        },

        push_order: function(ks_order, opts){
            var ks_pushed = ks_super_pos.push_order.call(this, ks_order, opts);
            if (ks_order){
                this.ks_update_product_qty_from_order(ks_order);
            }
            return ks_pushed;
        },

        ks_update_product_qty_from_order: function(ks_order){
            var self = this;
            ks_order.orderlines.forEach(line => {
                var ks_product = line.get_product();
                if(ks_product.type == 'product'){
                    ks_product.qty_available -= line.get_quantity();
                    self.ks_update_qty_by_product_id(self, [ks_product]);
                }
            });
        }
    });

    ks_screens.ActionpadWidget.include({

        renderElement: function(){
            var self = this;
            this._super();
            this.$('.pay').off('click');
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                if(ks_utils.ks_validate_order_items_availability(order, self.pos.config, self.gui)) {
                    var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                        return line.has_valid_product_lot();
                    });
                    if(!has_valid_product_lot){
                        self.gui.show_popup('confirm',{
                            'title': _t('Empty Serial/Lot Number'),
                            'body':  _t('One or more product(s) required serial/lot number.'),
                            confirm: function(){
                                self.gui.show_screen('payment');
                            },
                        });
                    }else{
                        self.gui.show_screen('payment');
                    }
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        }
    });

    ks_screens.ProductListWidget.include({
        calculate_cache_key: function(product, pricelist){
            return product.id + ',' + pricelist.id  + ',' + product.qty_available;
        },

        renderElement: function() {
            this._super();
            var self = this;
            var task;
            clearInterval(task);
            task = setTimeout(function () {
                $(".overlay").parent().addClass('pointer-none');
            }, 100);
        }
    });

    ks_screens.PaymentScreenWidget.include({

        validate_order: function(force_validation) {
            if (this.order_is_valid(force_validation) && ks_utils.ks_validate_order_items_availability(this.pos.get_order(), this.pos.config, this.gui)) {
                this.finalize_validation();
            }
        }
    });
});