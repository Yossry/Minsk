odoo.define("web.backend_falcon_theme", function(require) {
    "use strict";

    var Menu = require("web.Menu");
    var ajax = require("web.ajax");
    $(document).ready(function() {
        $(".o_sub_menu").prepend(
            "<span class='si-icons'><span></span><span class='s2'></span><span></span></spn>"
        );

        $(".o_sub_menu span.si-icons").click(function(e) {
            // Prevent the default action
            e.preventDefault();
            // Stop the click from bubbling
            e.stopPropagation();
            $("body").toggleClass("oe_leftbar_open");
        });
        setTimeout(function() {
            ajax.jsonRpc("/get_apps/menu", "call", {}).then(function(res) {
                // Console.log('res',res);
                $(".o_main_navbar")
                    .find("ul.o_menu_sections")
                    .append(res);
            });
        }, 400);
    });
    // Dom.initAutoMoreMenu(this.$section_placeholder, {
    //     console.log('self.$el.width()',self.$el.width());
    //     maxWidth: function () {
    //         return self.$el.width() - (self.$menu_apps.outerWidth(true) + self.$menu_brand_placeholder.outerWidth(true) + self.systray_menu.$el.outerWidth(true));
    //     },
    //     sizeClass: 'SM',
    // });

    return Menu.include({
        change_menu_section: function(primary_menu_id) {
            var res = this._super.apply(this, arguments);
            if (this.$menu_sections[primary_menu_id]) {
                this.$menu_sections[primary_menu_id].appendTo(
                    $("div.o_sub_menu > .o_sub_menu_content > ul.oe_secondary_menu")
                );
                if ($("ul.oe_secondary_menu").has("li").length === 0) {
                    $(".o_sub_menu").addClass("o_hidden");
                } else {
                    $(".o_sub_menu").removeClass("o_hidden");
                }
            }
            // <<< QTL EDIT
            // Display all sub-menus
            $(".o_sub_menu .dropdown-menu").show();
            // >>> QTL EDIT
            return res;
        },
        reflow: function(behavior) {
            var self = this;
            var $more_container = this.$("#menu_more_container").hide();
            var $more = this.$("#menu_more");
            var $systray = this.$el.parents().find(".oe_systray");

            // Pull all the items out of the more menu
            $more.children("li").insertBefore($more_container);

            // 'all_outside' beahavior should display all the items, so hide the more menu and exit
            if (behavior === "all_outside") {
                // Show list of menu items
                self.$el.show();
                this.$el.find("li").show();
                $more_container.hide();
                return;
            }

            // Hide all menu items
            var $toplevel_items = this.$el
                .find("li")
                .not($more_container)
                .not($systray.find("li"))
                .hide();
            // Show list of menu items (which is empty for now since all menu items are hidden)
            self.$el.show();
            $toplevel_items.each(function() {
                var remaining_space =
                    self.$el.parent().width() - $more_container.outerWidth();
                self.$el
                    .parent()
                    .children(":visible")
                    .each(function() {
                        remaining_space -= $(this).outerWidth();
                    });

                if ($(this).width() >= remaining_space) {
                    // The current item will be appended in more_container
                    return false;
                }
                // Show the current item in menu bar
                $(this).show();
            });
            $more.append($toplevel_items.filter(":hidden").show());
            $more_container.toggle(Boolean($more.children().length));
            // Hide toplevel item if there is only one
            var $toplevel = self.$el.children("li:visible");
            if ($toplevel.length === 1) {
                $toplevel.hide();
            }
        },
    });
});
