odoo.define('uppercrust_backend_theme.abstract_controller', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var core = require('web.core');
    var config = require('web.config');
    var QWeb = core.qweb;

    AbstractController.include({
        _renderSwitchButtons: function () {
            // add onclick event listener
            this._super.apply(this, arguments);
            var self = this;
            if (this.viewType !== 'form' && this.viewType !== 'list') {
                $('body').find('.ad_rightbar').removeClass('o_open_sidebar');
            }
            var views = _.filter(this.actionViews, {multiRecord: this.isMultiRecord});

            if (views.length <= 1) {
                return $();
            }

            var template = 'ControlPanel.SwitchButtons.Mobile';
            var $switchButtons = $(QWeb.render(template, {
                views: views,
            }));
            var $switchButtonsFiltered = $switchButtons.find('button');
            $switchButtonsFiltered.click(_.debounce(function (event) {
                var viewType = $(event.target).data('view-type');
                self.trigger_up('switch_view', {view_type: viewType});
            }, 200, true));
            // set active view's icon as view switcher button's icon
            var activeView = _.findWhere(views, {type: this.viewType});
            $switchButtons.find('.o_switch_view_button_icon').addClass('fa fa-lg ' + activeView.icon);
            return $switchButtons;
        },
    });

});