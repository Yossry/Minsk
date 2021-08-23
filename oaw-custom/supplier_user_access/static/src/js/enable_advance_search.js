odoo.define("supplier_user_access.EnableAdvanceSearch", function(require) {
    "use strict";

    var AbstractController = require("web.AbstractController");

    var EnableAdvanceSearch = AbstractController.include({
        _update: function(state) {
            var def = this._super(state);
            this.getSession()
                .user_has_group("stock.group_stock_user")
                .then(function(has_group) {
                    if (has_group) {
                        $("div.o_cp_right").show();
                        $("div.o_mobile_search_filter").show();
                        $("span.o_searchview_more").show();
                    } else {
                        $("div.o_search_options").hide();
                        $("div.o_mobile_search_filter").hide();
                        $("span.o_searchview_more").hide();
                        $("div.o_cp_right").show();
                    }
                });
            return def;
        },
    });

    return EnableAdvanceSearch;
});
