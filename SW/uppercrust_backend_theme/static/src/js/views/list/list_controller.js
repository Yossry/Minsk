odoo.define('uppercrust_backend_theme.ListController', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var ListRenderer = require('web.ListRenderer');
    var Sidebar = require('web.Sidebar');

    ListController.include({
        _doUpdateSidebar: function () {
            if (this.selectedRecords.length > 0 && this.sidebar.$el.hasClass('o_drw_in')) {
                $('body').find('.ad_rightbar').addClass('o_open_sidebar');
            } else {
                $('body').find('.ad_rightbar').removeClass('o_open_sidebar');
            }
        },
        _toggleSidebar: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.sidebar) {
                this.sidebar.do_toggle(this.selectedRecords.length > 0);
                this.sidebar.$el.addClass('o_drw_in');
                this._doUpdateSidebar();
            }
        },
    });
});
