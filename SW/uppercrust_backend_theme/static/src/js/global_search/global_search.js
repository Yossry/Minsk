odoo.define('uppercrust_backend_theme.global_search', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var GlobalAutoComplete = require('uppercrust_backend_theme.GlobalAutoComplete');

    var GlobalSearch = Widget.extend({
        template: 'GlobalSearch',
        events: {
            'input input.global-search': function (e) {
                clearTimeout(this.timer);
                var self = this;
                this.timer = setTimeout(this.get_data_auto.bind(this), 200);
                this.$input_val = $(e.currentTarget).val();
                if (!self.$('input.global-search').val()) {
                    $('.user-dropdown.input-group').find('.cu_close').css('display', 'none')
                    $('.user-dropdown.input-group').find('.cu_search').css('display', 'block')
                } else {
                    if ($('.user-dropdown.input-group').find('.cu_close').css('display') == 'none') {
                        $('.user-dropdown.input-group').find('.cu_close').css('display', 'block')
                        $('.user-dropdown.input-group').find('.cu_search').css('display', 'none')
                    }
                }
            },
            'click input.global-search': function (e) {
                e.preventDefault();
                e.stopPropagation();
                this.autocomplete.remove_focus_element()
            },
            'click .fa-times': function (e) {
                $('.user-dropdown.input-group').find('.cu_close').css('display', 'none')
                $('.user-dropdown.input-group').find('.cu_search').css('display', 'block')
                this.$el.find('.global-search').val('')
            },
        },
        init: function (parent) {
            this._super(parent);
            this.models = null;
            this.$input_val = '';
            this.autocomplete = null;
            this.timer = 0
        },
        get_data_auto: function () {
            var self = this
            if (!self.$('input.global-search').val()) {
                self.autocomplete.close()
                return;
            }
            self.autocomplete.search_string = self.$('input.global-search').val()
            return self._rpc({
                route: '/globalsearch/model_fields',
                params: {}
            }).then(function (r) {
                return self.autocomplete.search(self.$('input.global-search').val(), r)
            });
        },
        start: function () {
            var self = this
            self._super.apply(this, arguments);
            self.values = []
            self.autocomplete = new GlobalAutoComplete(this, {
                get_search_element: function () {
                    return self.$('input.global-search');
                },
                get_search_string: function () {
                    return self.$('input.global-search').val();
                },
            });
            self.timer = 0;
            self.autocomplete.appendTo(self.$el);
        },
    });
    SystrayMenu.Items.push(GlobalSearch)
    return GlobalSearch;
});