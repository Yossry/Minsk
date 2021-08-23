// odoo Menu inherit Open time has Children submenu add.
odoo.define('uppercrust_backend_theme.Menu', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Menu = require('web.Menu');
    var UserMenu = require('web.UserMenu');
    var QuickMenu = require('uppercrust_backend_theme.QuickMenu');
    var GlobalSearch = require('uppercrust_backend_theme.global_search');
    var config = require('web.config');
    var session = require('web.session');
    var AppsMenu = require('web.AppsMenu');
    var SystrayMenu = require('web.SystrayMenu');

    var QWeb = core.qweb;

    var LogoutMessage = Widget.extend({
        template: 'LogoutMessage',
        events: {
            'click  a.oe_cu_logout_yes': '_onClickLogout',
            'click  .mb-control-close': '_onClickClose',
        },
        init: function (parent) {
            this._super(parent);
        },
        _onClickLogout: function (e) {
            var self = this;
            self.getParent()._onMenuLogout();
        },
        _onClickClose: function (e) {
            this.$el.remove();
        }
    });

    var MenuGlobalSearch = Widget.extend({
        template: 'menu.GlobalSearch',
        events: {
            'click  .oe_back_btn': '_closeGloblesearch',
            'click  ul.o_glonal_search_dropdown:not(.oe_back_btn)': '_onClickInside',
        },
        init: function (parent) {
            this._super(parent);
        },
        _closeGloblesearch: function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(e.currentTarget).parents('.o_gb_search').removeClass('show');
            $(e.currentTarget).parent('.o_glonal_search_dropdown').removeClass('show');
        },
        _onClickInside: function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.offsetX < this.$('.o_glonal_search_dropdown')[0].offsetWidth) {
                $(e.currentTarget).parents('.o_gb_search').addClass('open');
            } else {
                $(e.currentTarget).parents('.o_gb_search').removeClass('open');
            }
        },

    });

    UserMenu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var $avatar = self.$('.oe_topbar_avatar');
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image',
                    id: session.uid,
                });
                $avatar.attr('src', avatar_src);
                self.$el.on('click', 'li a.o_menu_logout', function (ev) {
                    ev.preventDefault();
                    return new LogoutMessage(self).appendTo(self.$el.closest('body'));
                });
            });
        },
    });

    Menu.include({
        events: _.extend({}, Menu.prototype.events, {
            'click #menu_toggle': '_onMenuToggleClicked',
            'click #children_toggle': '_onSubmenuToggleClicked',
            'click #av_full_view': '_onFullViewClicked',
            'click .oe_back_btn': '_onMenuClose',
            'click .o_app': '_onMenuClose',
            'click a[data-menu]': '_onMenuClose',
        }),
        init: function (parent, menu_data) {
            this._super.apply(this, arguments);
            this.company_id = session.company_id;
        },
        start: function () {
            var self = this;

            this.$menu_apps = this.$('.o_menu_apps');
            this.$menu_brand_placeholder = this.$('.o_menu_brand');
            this.$section_placeholder = this.$('.o_menu_sections');
            this.$children_toggle = this.$('#children_toggle')
            // Navbar's menus event handlers
            var on_secondary_menu_click = function (ev) {
                ev.preventDefault();
                var menu_id = $(ev.currentTarget).data('menu');
                var action_id = $(ev.currentTarget).data('action-id');
                self._on_secondary_menu_click(menu_id, action_id);
            };
            var menu_ids = _.keys(this.$menu_sections);
            var primary_menu_id, $section;
            for (var i = 0; i < menu_ids.length; i++) {
                primary_menu_id = menu_ids[i];
                $section = this.$menu_sections[primary_menu_id];
                $section.on('click', 'a[data-menu]', self, on_secondary_menu_click.bind(this));
            }

            // Apps Menu
            this._appsMenu = new AppsMenu(self, this.menu_data);
            this._appsMenu.appendTo(this.$menu_apps);

            // Systray Menu
            this.systray_menu = new SystrayMenu(this);
            this.systray_menu.attachTo(this.$('.o_menu_systray'));
            this._loadQuickMenu();
            this._resizeMenu();
            $(window).on("resize", this._resizeMenu);
        },
        _onMenuToggleClicked: function (e) {
            $('body').removeClass('ad_open_childmenu').toggleClass('nav-sm');
            $(this).toggleClass('active');
        },
        _onSubmenuToggleClicked: function (e) {
            $('body').removeClass('nav-sm').toggleClass('ad_open_childmenu');
            $(this).toggleClass('active');
        },
        change_menu_section: function (primary_menu_id) {
            if (!this.$menu_sections[primary_menu_id]) {
                this._updateMenuBrand();
                return; // unknown menu_id
            }

            if (this.current_primary_menu === primary_menu_id) {
                return; // already in that menu
            }

            if (this.current_primary_menu) {
                this.$menu_sections[this.current_primary_menu].detach();
            }

            // Get back the application name
            for (var i = 0; i < this.menu_data.children.length; i++) {
                if (this.menu_data.children[i].id === primary_menu_id) {
                    this._updateMenuBrand(this.menu_data.children[i].name);
                    break;
                }
            }

            // Selcted Menu
            var submenu_data = _.findWhere(this.menu_data.children, {id: primary_menu_id});
            var $submenu_title = $(QWeb.render('SubmenuTitle', {
                selected_menu: submenu_data,
            }));
            this.$section_placeholder.html($submenu_title);
            $('<div>', {
                class: 'o_submenu_list',
            }).append(this.$menu_sections[primary_menu_id]).appendTo(this.$section_placeholder);
            this.current_primary_menu = primary_menu_id;
            $('body').toggleClass('ad_nochild', !submenu_data.children.length);

            core.bus.trigger('resize');
        },
        _updateMenuBrand: function (brandName) {
            if (brandName) {
                this.$menu_brand_placeholder.text(brandName).show();
                this.$section_placeholder.show();
                this.$children_toggle.show()
            } else {
                this.$menu_brand_placeholder.hide()
                this.$section_placeholder.hide();
                this.$children_toggle.hide()
            }
        },
        _onFullViewClicked: function (e) {
            $('body').toggleClass('ad_full_view');
        },
        _onMenuClose: function (e) {
            $('body').removeClass('ad_open_childmenu').removeClass('nav-sm');
        },
        _resizeMenu: function(e){
            var leftBarHeight = $(window).outerHeight();
            var MenuiconHeight = $('.oe_menu_layout').outerHeight();
            var MenuSystrayHeight = $('.o_menu_systray').outerHeight();
            var IconHeight = $('.o_toggle_menu').outerHeight();
            var TotalHeight = leftBarHeight - (MenuiconHeight + MenuSystrayHeight + IconHeight)
            var allReadyBind = $('.o_menu_systray').hasClass('dropdown-menu');
            var $dropdownMenu = $('.o_menu_systray');
            var $extraItemsToggle = $('<li/>', {class: 'oe_wrap_menus'});
            var $mainHightset = $('.o_main_navbar');
            if(TotalHeight < 1 && !allReadyBind){
                $dropdownMenu.addClass('dropdown-menu');
                    $extraItemsToggle.append($('<a/>', {role: 'button', href: '#', class: 'nav-link dropdown-toggle o-no-caret o_mobile_sys', 'data-toggle': 'dropdown', 'aria-expanded': false})
                        .append($('<i/>', {class: 'fa fa-ellipsis-h'})))
                    .append($dropdownMenu);
                $extraItemsToggle.insertAfter($('.oe_menu_layout').last());
                $mainHightset.addClass('oe_mobile_view');
            }
            else if(TotalHeight >= 1){
                $dropdownMenu.removeClass('dropdown-menu show');
                $('.oe_wrap_menus').replaceWith($dropdownMenu);
                $mainHightset.removeClass('oe_mobile_view');
            }
        },
        _loadQuickMenu: function () {
            var self = this;
            new QuickMenu(self).appendTo(this.$el.parents('.o_web_client').find('.oe_menu_layout'));
            this.$el.parents('.o_web_client').find('.oe_systray li.o_global_search').remove();
            new MenuGlobalSearch(self).appendTo(this.$el.find('.o_quick_menu'));
            new GlobalSearch(self).appendTo(this.$el.find('.o_gb_search ul'));
        },
    });
});