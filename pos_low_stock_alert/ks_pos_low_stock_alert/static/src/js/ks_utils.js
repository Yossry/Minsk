/*
    @Author: KSOLVES India Private Limited
    @Email: sales@ksolves.com
*/

odoo.define('ks_pos_low_stock_alert.utils', function (require) {
    "use strict";

    var _t = require('web.core')._t;

    function ks_validate_order_items_availability(ks_order, config, ks_gui) {

        var isValid = true, ks_order_line;

        if(!config.allow_order_when_product_out_of_stock) {
            for(var i = 0; i < ks_order.get_orderlines().length ; i++) {
                ks_order_line = ks_order.get_orderlines()[i];
                if(ks_order_line.get_product().type == 'product' && (ks_order_line.get_quantity() > ks_order_line.get_product().qty_available)) {
                    isValid = false;
                    break;
                }
            }
        }
        if(!isValid){
            ks_gui.show_popup('error',{
                'title': _t('Cannot order a product more than its availability'),
                'body':  _t(ks_order_line.get_product().display_name + ' has only ' + ks_order_line.get_product().qty_available + ' items available. \n You\'re trying to order ' + ks_order_line.get_quantity() + '.'),
            });
        }
        return isValid;
    }

    return {
        ks_validate_order_items_availability: ks_validate_order_items_availability
    }
});