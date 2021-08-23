odoo.define("base_company_logo_visibility.ShowCompanyLogo", function(require) {
    "use strict";

    var Widget = require("web.Widget");
    var SystrayMenu = require("web.SystrayMenu");

    var ShowCompanyLogo = Widget.extend({
        start: function() {
            this.getSession()
                .user_has_group("base_company_logo_visibility.group_company_logo")
                .then(function(has_group) {
                    if (has_group) {
                        $("div.o_theme_logo").show();
                    }
                });
            return this._super.apply(this, arguments);
        },
    });
    SystrayMenu.Items.push(ShowCompanyLogo);
    return ShowCompanyLogo;
});
