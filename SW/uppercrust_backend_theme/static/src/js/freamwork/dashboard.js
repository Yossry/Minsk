odoo.define('uppercrust_backend_theme.DashboardCustomizeTheme', function (require) {
    "use strict";

    var core = require('web.core');
    var web_settings_dashboard = require('web_settings_dashboard');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var _t = core._t;

    var fields = {
        'leftbar_color': 'LeftBar',
        'menu_color': 'Menu',
        'buttons_color': 'Button',
        'button_box': 'Button Box',
        'heading_color': 'Heading',
        'label_color': 'Label',
        'label_value_color': 'Label Value',
        'link_color': 'Link Color',
        'panel_title_color': 'Panel Title',
        'tooltip_color': 'Tooltip',
        'border_color': 'Border'
    };

    var status_colors = {
        'tag_info': '00b3e5',
        'tag_danger': '#ca0c05',
        'tag_success': '#00aa00',
        'tag_warning': '#e47e01',
        'tag_primary': '#005ba9',
        'tag_muted': '#717171',
    };

    web_settings_dashboard.Dashboard.include({
        load: function (dashboards) {
            var self = this;
            var loading_done = new $.Deferred();
            this._rpc({route: '/web_settings_dashboard/data'})
                    .then(function (data) {
                        // Load each dashboard
                        var all_dashboards_defs = [];
                        _.each(dashboards, function (dashboard) {
                            var dashboard_def = self['load_' + dashboard](data);
                            if (dashboard_def) {
                                all_dashboards_defs.push(dashboard_def);
                            }
                        });
                        var dashboard_def = self['load_customize_theme'](data);
                        if (dashboard_def) {
                            all_dashboards_defs.push(dashboard_def);
                        }
                        // Resolve loading_done when all dashboards defs are resolved
                        $.when.apply($, all_dashboards_defs).then(function () {
                            loading_done.resolve();
                        });
                    });
            return loading_done;
        },
        load_customize_theme: function () {
            return new DashboardCustomizeTheme(this).replace(this.$('.o_web_settings_dashboard_customize_theme'));
        },
    });
    var CustomizeThemeDialog = Dialog.extend({
        dialog_title: _t('Customize Theme'),
        template: "CustomizeTheme",
        events: {
            'click .o_add_theme': '_onClickAddRecord',
            'click ul.oe_theme_colorpicker li .o_view': '_onClickSelectTheme',
            'click ul.oe_theme_colorpicker li .o_remove': '_onClickRemoveTheme',
        },
        init: function (parent, result, is_status_tags) {
            var self = this;
            this.result = result;
            this.is_status_tags = is_status_tags;
            this._super(parent, {
                title: _t('Customize Theme'),
                buttons: [{
                    text: _t('Apply'),
                    classes: 'btn-primary',
                    click: function () {
                        self._onClickSaveTheme();
                    },
                }, {
                    text: _t('Cancel'),
                    close: true,
                }],
            });
        },
        start: function () {
            var self = this;
            this.form_values = {};
            this.invalidFields = [];
            this.$('.o_colorpicker').each(function () {
                $(this).minicolors({
                    control: 'hue',
                    inline: false,
                    letterCase: 'lowercase',
                    opacity: false,
                    theme: 'bootstrap'
                });
            });
            if (!_.isEmpty(this.result)) {
                this.current_theme = _.findWhere(this.result, {'selected': true});
                if (!_.isUndefined(this.current_theme)) {
                    self._fetchThemeData(self.current_theme.id);
                }
            }
            return this._super.apply(this, arguments);
        },
        _onClickAddRecord: function () {
            this.$el.addClass('o_new_record');
            this.$('.o_control_form').find('input').minicolors('value', '');
            if (this.is_status_tags) {
                this.$('.o_breadcrumb_form').find('input').minicolors('value', '');
            }
        },
        _setSelectedTheme: function (result) {
            var self = this;
            this.$el.removeClass('o_new_record');
            _.each(result, function (value, field) {
                self.$('input[name=' + field + ']').minicolors('value', value);
            })
        },
        _fetchThemeData: function (theme_id) {
            var self = this;
            var form_fields = _.keys(fields);
            if (self.is_status_tags) {
                form_fields.push.apply(form_fields, _.keys(status_colors));
            }
            this._rpc({
                model: 'ir.web.theme',
                method: 'search_read',
                domain: [['id', '=', theme_id]],
                fields: form_fields,
            }).then(function (result) {
                self._setSelectedTheme(result[0]);
            });
        },
        _removeTheme: function ($li, res_id) {
            var self = this;
            self._rpc({
                model: 'ir.web.theme',
                method: 'unlink',
                args: [parseInt(res_id, 10)],
            }).then(function (value) {
                $li.remove();
                self.do_notify(_t("Sucsess"), _t("Theme removed successfully."));
            })
        },
        _onClickSelectTheme: function (e) {
            var self = this;
            this.$el.find('ul li').removeClass('selected');
            $(e.currentTarget).parents('li').addClass('selected');
            var res_id = $(e.currentTarget).parents('li').find('span').data('id');
            if (res_id !== 0) {
                self._fetchThemeData(res_id);
            }
        },
        _onClickRemoveTheme: function (e) {
            var self = this;
            var res = confirm(_t("Do you want to delete this record?"));
            if (res) {
                var res_id = $(e.currentTarget).parents('li').find('span').data('id');
                if (res_id !== 0) {
                    var $li = $(e.currentTarget).parents('li');
                    self._removeTheme($li, res_id);
                }
            }

        },
        _createRecord: function (form_values) {
            return this._rpc({
                model: 'ir.web.theme',
                method: 'create',
                args: [form_values],
                kwargs: {context: session.user_context},
            });
        },
        _updateRecord: function (theme_id, form_values) {
            return this._rpc({
                model: 'ir.web.theme',
                method: 'write',
                args: [[theme_id], form_values],
            });
        },
        _changeCurruntTheme: function (theme_id) {
            var self = this;
            return this._rpc({
                model: 'ir.web.theme',
                method: 'set_customize_theme',
                args: [[], theme_id, self.form_values],
            }).then(function () {
                location.reload();
            });
        },
        _notifyInvalidFields: function (invalidFields) {
            var warnings = invalidFields.map(function (fieldName) {
                var fieldStr = fields[fieldName];
                return _.str.sprintf('<li>%s</li>', _.escape(fieldStr));
            });
            warnings.unshift('<ul>');
            warnings.push('</ul>');
            this.do_warn(_t("The following fields are invalid:"), warnings.join(''));
        },
        _doChangeTheme: function (theme_id) {
            var self = this;
            self._changeCurruntTheme(theme_id).then(function () {
                self.do_notify(_t("Sucsess"), _t("Theme customized successfully."));
                self.close(true);
                return;
            });
        },
        _onClickSaveTheme: function () {
            var self = this, theme_id;
            var form_fields = this.$('.o_control_form').serializeArray();
            _.each(form_fields, function (input) {
                if (input.value !== '') {
                    self.form_values[input.name] = input.value;
                } else {
                    self.invalidFields.push(input.name);
                }
            });
            if (self.is_status_tags) {
                var form_status_fields = this.$('.o_breadcrumb_form').serializeArray();
                _.each(form_status_fields, function (input) {
                    if (input.value !== '') {
                        self.form_values[input.name] = input.value;
                    } else {
                        self.form_values[input.name] = status_colors[input.name];
                    }
                });
            }
            if (!_.isEmpty(self.invalidFields)) {
                self._notifyInvalidFields(self.invalidFields);
                self.invalidFields = [];
                return false;
            } else {
                if (self.$el.hasClass('o_new_record')) {
                    self._createRecord(self.form_values).then(function (theme_id) {
                        self._doChangeTheme(theme_id);
                    })
                } else {
                    theme_id = this.$el.find('ul li.selected span').data('id');
                    if (theme_id && !_.isUndefined(theme_id) && theme_id !== 0) {
                        self._updateRecord(parseInt(theme_id), self.form_values).then(function () {
                            self._doChangeTheme(parseInt(theme_id));
                        })
                    }
                }

            }
        }
    });
    var DashboardCustomizeTheme = Widget.extend({
        template: 'DashboardThemeColors',
        events: {
            'click .o_setup_theme': '_onClickSetupTheme'
        },
        init: function (parent) {
            this.parent = parent;
            this.is_status_tags = false;
            this._super.apply(this, arguments);
        },
        _checkStatusbar: function () {
            var self = this;
            return self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['web_status_tags.is_status_tags']
            }).then(function (is_status_tags) {
                return self.is_status_tags = (parseInt(is_status_tags) === 1);
            });
        },
        _onClickSetupTheme: function () {
            var self = this;
            self._checkStatusbar().then(function (is_status_tags) {
                var form_fields = _.keys(fields);
                if (is_status_tags) {
                    form_fields.push.apply(form_fields, _.keys(status_colors));
                }
                self._rpc({
                    model: 'ir.web.theme',
                    method: 'search_read',
                    fields: form_fields,
                }).then(function (result) {
                    self._rpc({
                        model: 'ir.config_parameter',
                        method: 'get_param',
                        args: ['uppercrust_backend_theme.selected_theme']
                    }).then(function (theme_id) {
                        _.each(result, function (rec, i) {
                            result[i]['selected'] = (rec.id === parseInt(theme_id));
                        });
                        return new CustomizeThemeDialog(self, result, is_status_tags).open();
                    });
                })

            });
        },
    });
    return {
        CustomizeThemeDialog: CustomizeThemeDialog,
        DashboardCustomizeTheme: DashboardCustomizeTheme,
    };

});
