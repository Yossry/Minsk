odoo.define('uppercrust_backend_theme.Breadcrumb', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var relational_fields = require('web.relational_fields');
    var Qweb = core.qweb;

    var _t = core._t;

    relational_fields.FieldStatus.include({
        _render: function () {
            var self = this;
            if (config.device.isMobile) {
                var state_info = _.findWhere(self.status_information, {selected: true});
                this.$el.html(Qweb.render("Breadcrumb.mobile", {
                    selection: self.status_information,
                    state_info: state_info,
                    clickable: !!self.attrs.clickable,
                }));
            } else {
                return this._super.apply(this, arguments);
            }
        },
    });
});
