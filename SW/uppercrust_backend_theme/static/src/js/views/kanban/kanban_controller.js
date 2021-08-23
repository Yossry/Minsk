odoo.define('uppercrust_backend_theme.KanbanController', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');

    KanbanController.include({
        _doUpdateSidebar: function () {
            var $body = $('body');
            if ($body.hasClass('ad_open_search')) {
                $body.find('.ad_rightbar').addClass('o_open_sidebar');
            } else {
                $body.find('.ad_rightbar').removeClass('o_open_sidebar');
            }
        },
        _update: function () {
            this._updateButtons();
            this._doUpdateSidebar();
            return this._super.apply(this, arguments);
        },
    });
});
