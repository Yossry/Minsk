// odoo Menu inherit menuge filter view option
// events view inherit
odoo.define('uppercrust_backend_theme.SearchView', function (require) {
    "use strict";

    var core = require('web.core');
    var config = require('web.config');
    var SearchView = require('web.SearchView');

    SearchView.include({
        init: function (parent, dataset, fvg, options) {
            this._super.apply(this, arguments);
            this.view = parent;
            this.visible_filters = false;
        },
        start: function () {
            var self = this;
            return this._super().then(function() {
                self.$buttons.find('.o_dropdown:first-child').addClass('ad_active show');
                self.$buttons.find('.o_dropdown_toggler_btn').on('click', self._dropdownToggler.bind(self))
            });
        },
        _dropdownToggler: function(e){
            var self = this;
            var $searchoption = self.$buttons.parent()
                    .find('.ad_active').removeClass('ad_active');
            var $clickbutton = $(e.target).parent().hasClass('o_dropdown');
            if ($clickbutton) {
                $(e.target).parent().addClass('ad_active');
            } else {
                $(e.target).parent().parent().addClass('ad_active');
            }
        },
        toggle_visibility: function (is_visible) {
            this.do_toggle(!this.headless && is_visible);
            if (this.$buttons) {
                this.$buttons.parent('.o_search_options').toggle(!this.headless && is_visible && this.visible_filters);
            }
            this._focusInput();

        },
        toggle_buttons: function (is_visible) {
            this.visible_filters = is_visible || !this.visible_filters;
            if (this.$buttons)  {
                this.$buttons.parent('.o_search_options').toggle(this.visible_filters);
                this.$buttons.parents('.ad_rightbar').toggleClass('ad_open_search');
            }
            if(this.view.controllers){
                var activeView = this._getActiveView();
                if(activeView && activeView[0].viewType === 'graph'){
                    core.bus.trigger('toggle_graph_sidebar', this.visible_filters);
                }
            }
        },
        _getActiveView: function(){
            var self = this;
            return _.map(this.view.controllerStack, function (controllerID) {
                return {
                    viewType: self.view.controllers[controllerID].viewType,
                    controllerID: controllerID,
                };
            });
        },
        renderFacets: function (collection, model, options) {
            var self = this;
            this._super.apply(this, arguments);
            var search_area = 0;
            var device_width = window.innerWidth;
            _.each(this.input_subviews, function (childView) {
                if (childView.$el[0].localName !== 'input') {
                    search_area += childView.$el[0].clientWidth;
                }
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || config.device.size_class == config.device.SIZES.xs){
                    if (search_area > (device_width - 240) && childView.$el[0].localName !== 'input') {
                        childView.$el.appendTo(self.$('.o_search_rec_ul'))
                    }
                }else{
                    if (search_area > ((device_width / 2) - 250) && childView.$el[0].localName !== 'input') {
                        childView.$el.appendTo(self.$('.o_search_rec_ul'))
                    }
                }
                if (!_.isEmpty(self.$('.o_search_rec_ul').html())) {
                    !self.$el.hasClass('show') ? self.$el.addClass('show') : false;
                    self.$('.o_search_recs').removeClass('hidden');
                    self.$('.o_search_rec_ul').removeClass('hidden').addClass('show');
                } else {
                    self.$('.o_search_recs').addClass('hidden');
                    self.$('.o_search_rec_ul').addClass('hidden');
                }
            });
        }
    });
});