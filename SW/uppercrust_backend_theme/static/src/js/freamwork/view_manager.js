odoo.define('uppercrust_backend_theme.AbstractController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');

    AbstractController.include({
        _renderSwitchButtons: function (old_view) {
            if (this.viewType !== 'form' && this.viewType !== 'list') {
                $('body').find('.ad_rightbar').removeClass('o_open_sidebar');
            }
            return this._super.apply(this, arguments)
        },
    });
});