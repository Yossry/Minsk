/* Copyright 2018 Tecnativa - Jairo Llopis
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_bravo12', function (require) {
    'use strict';

    var AbstractWebClient = require("web.AbstractWebClient");
    var AppsMenu = require("web.AppsMenu");
    var config = require("web.config");
    var core = require("web.core");
    var FormRenderer = require('web.FormRenderer');
    var Menu = require("web.Menu");
    var RelationalFields = require('web.relational_fields');

    
    function findNames (memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, findNames, memo);
        }
        return memo;
    }

    AppsMenu.include({
        events: _.extend({
            "keydown .search-input input": "_searchResultsNavigate",
            "click .o-menu-search-result": "_searchResultChosen",
            "shown.bs.dropdown": "_searchFocus",
            "hidden.bs.dropdown": "_searchReset",
        }, AppsMenu.prototype.events),

        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            // Keep base64 icon for main menus
            for (var n in this._apps) {
                this._apps[n].web_icon_data =
                    menuData.children[n].web_icon_data;
            }
            // Store menu data in a format searchable by fuzzy.js
            this._searchableMenus = _.reduce(
                menuData.children,
                findNames,
                {}
            );
            // Search only after timeout, for fast typers
            this._search_def = $.Deferred();
        },

        /**
         * @override
         */
        start: function () {
            this.$search_container = this.$(".search-container");
            this.$search_input = this.$(".search-input input");
            this.$search_results = this.$(".search-results");
            return this._super.apply(this, arguments);
        },

        _menuInfo: function (key) {
            var original = this._searchableMenus[key];
            return _.extend({
                action_id: parseInt(original.action.split(',')[1], 10),
            }, original);
        },

        _searchFocus: function () {
            if (!config.device.isMobile) {
                this.$search_input.focus();
            }
        },

        /**
         * Reset search input and results
         */
        _searchReset: function () {
            this.$search_container.removeClass("has-results");
            this.$search_results.empty();
            this.$search_input.val("");
        },

        /**
         * Schedule a search on current menu items.
         */
        _searchMenusSchedule: function () {
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 50);
            this._search_def.done(this._searchMenus.bind(this));
        },

        /**
         * Search among available menu items, and render that search.
         */
        _searchMenus: function () {
            var query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("has-results");
                this.$search_results.empty();
                return;
            }
            var results = fuzzy.filter(
                query,
                _.keys(this._searchableMenus),
                {
                    pre: "<b>",
                    post: "</b>",
                }
            );
            this.$search_container.toggleClass(
                "has-results",
                Boolean(results.length)
            );
            this.$search_results.html(
                core.qweb.render(
                    "web_bravo12.MenuSearchResults",
                    {
                        results: results,
                        widget: this,
                    }
                )
            );
        },

        /**
         * Use chooses a search result, so we navigate to that menu
         *
         * @param {jQuery.Event} event
         */
        _searchResultChosen: function (event) {
            event.preventDefault();
            var $result = $(event.currentTarget),
                text = $result.text().trim(),
                data = $result.data(),
                suffix = ~text.indexOf("/") ? "/" : "";
            // Load the menu view
            this.trigger_up("menu_clicked", {
                action_id: data.actionId,
                id: data.menuId,
                previous_menu_id: data.parentId,
            });
            // Find app that owns the chosen menu
            var app = _.find(this._apps, function (_app) {
                return text.indexOf(_app.name + suffix) === 0;
            });
            // Update navbar menus
            core.bus.trigger("change_menu_section", app.menuID);
        },

        /**
         * Navigate among search results
         *
         * @param {jQuery.Event} event
         */
        _searchResultsNavigate: function (event) {
            // Exit soon when not navigating results
            if (this.$search_results.html().trim() === "") {
                // Just in case it is the 1st search
                this._searchMenusSchedule();
                return;
            }
            // Find current results and active element (1st by default)
            var all = this.$search_results.find(".o-menu-search-result"),
                pre_focused = all.filter(".active") || $(all[0]),
                offset = all.index(pre_focused),
                key = event.key;
            // Transform tab presses in arrow presses
            if (key === "Tab") {
                event.preventDefault();
                key = event.shiftKey ? "ArrowUp" : "ArrowDown";
            }
            switch (key) {
            // Pressing enter is the same as clicking on the active element
            case "Enter":
                pre_focused.click();
                break;
            // Navigate up or down
            case "ArrowUp":
                offset--;
                break;
            case "ArrowDown":
                offset++;
                break;
            // Other keys trigger a search
            default:
                // All keys that write a character have length 1
                if (key.length === 1 || key === "Backspace") {
                    this._searchMenusSchedule();
                }
                return;
            }
            // Allow looping on results
            if (offset < 0) {
                offset = all.length + offset;
            } else if (offset >= all.length) {
                offset -= all.length;
            }
            // Switch active element
            var new_focused = $(all[offset]);
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            this.$search_results.scrollTo(new_focused, {
                offset: {
                    top: this.$search_results.height() * -0.5,
                },
            });
        },
    });

    Menu.include({
        events: _.extend({
            // Clicking a hamburger menu item should close the hamburger
            "click .o_menu_sections [role=menuitem]": "_hideMobileSubmenus",
            // Opening any dropdown in the navbar should hide the hamburger
            "show.bs.dropdown .o_menu_systray, .o_menu_apps":
                "_hideMobileSubmenus",
        }, Menu.prototype.events),

        start: function () {
            this.$menu_toggle = this.$(".o-menu-toggle");
            this.$menu_brand_placeholder = this.$('.o_menu_brand');
            this.$section_placeholder = this.$('.o_menu_sections');
            return this._super.apply(this, arguments);
        },

        /**
         * Hide menus for current app if you're in mobile
         */
        _hideMobileSubmenus: function () {
            if (
                this.$menu_toggle.is(":visible") &&
                this.$section_placeholder.is(":visible")
            ) {
                this.$section_placeholder.collapse("hide");
            }
        },

        /**
         * No menu brand in mobiles
         *
         * @override
         */
        _updateMenuBrand: function () {
            if (!config.device.isMobile) {
                return this._super.apply(this, arguments);
            }
        },
    });

    RelationalFields.FieldStatus.include({

        /**
         * Fold all on mobiles.
         *
         * @override
         */
        _setState: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                _.map(this.status_information, function (value) {
                    value.fold = true;
                });
            }
        },
    });

    // Responsive view "action" buttons
    FormRenderer.include({

        /**
         * In mobiles, put all statusbar buttons in a dropdown.
         *
         * @override
         */
        _renderHeaderButtons: function () {
            var $buttons = this._super.apply(this, arguments);
            if (
                !config.device.isMobile ||
                !$buttons.is(":has(>:not(.o_invisible_modifier))")
            ) {
                return $buttons;
            }

            // $buttons must be appended by JS because all events are bound
            $buttons.addClass("dropdown-menu");
            var $dropdown = $(core.qweb.render(
                'web_bravo12.MenuStatusbarButtons'
            ));
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            return $dropdown;
        },
    });


    var KeyboardNavigationShiftAltMixin = {

        _shiftPressed: function (keyEvent) {
            var alt = keyEvent.altKey || keyEvent.key === "Alt",
                newEvent = _.extend({}, keyEvent),
                shift = keyEvent.shiftKey || keyEvent.key === "Shift";
            // Mock event to make it seem like Alt is not pressed
            if (alt && !shift) {
                newEvent.altKey = false;
                if (newEvent.key === "Alt") {
                    newEvent.key = "Shift";
                }
            }
            return newEvent;
        },

        _onKeyDown: function (keyDownEvent) {
            return this._super(this._shiftPressed(keyDownEvent));
        },

        _onKeyUp: function (keyUpEvent) {
            return this._super(this._shiftPressed(keyUpEvent));
        },
        //hack to redirect to main screen
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function(res) {
                if (_.isEmpty($.bbq.getState(true))) {
                    self.$('.full').trigger('click');
                }
            });
        }
    };

    // Include the SHIFT+ALT mixin wherever
    // `KeyboardNavigationMixin` is used upstream
    AbstractWebClient.include(KeyboardNavigationShiftAltMixin);

});

/* Copyright 2017 Openworx.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_bravo12.sidebar-toggle', function (require) {
    "use strict";
    
    var session = require('web.session');
    var rpc = require('web.rpc');
    var id = session.uid;
    rpc.query({
                model: 'res.users',
                method: 'read',
                args: [[id], ['sidebar_visible']],
            }).then(function(res) {
                var dbfield = res[0];
                var toggle = dbfield.sidebar_visible;
                if (toggle === true) {
                    $("#app-sidebar").removeClass("toggle-sidebar");
                } else {
                    $("#app-sidebar").addClass("toggle-sidebar");
                };
    });
                             
});

odoo.define('backend_theme_v12.Sidebar', function(require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');
    $(function() {
    (function($) {
        $.addDebug = function(url) {
        url = url.replace(/(.{4})/, "$1?debug");
        return url;
        }
        $.addDebugWithAssets = function(url) {
        url = url.replace(/(.{4})/, "$1?debug=assets");
        return url;
        }
        $.delDebug = function(url) {
        var str = url.match(/web(\S*)#/);
        url = url.replace("str/g", "");
        return url;
        }
    }) (jQuery);
        $("#sidebar a").each(function() {
            var url = $(this).attr('href');
            if (session.debug == 1) $(this).attr('href', $.addDebug(url));
            if (session.debug == 'assets') $(this).attr('href', $.addDebugWithAssets(url));
            if (session.debug == false) $(this).attr('href', $.delDebug(url));
        });
    });
});