odoo.define('uppercrust_backend_theme.GlobalAutoComplete', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');

    return Widget.extend({
        template: "GlobalSearch.AutoComplete",
        // Parameters for autocomplete constructor:
        //
        // parent: this is used to detect keyboard events
        //
        // options.select: function (ev, {item: {facet:facet}}).  Autocomplete widget will call
        //      that function when a selection is made by the user
        // options.get_search_string: function ().  This function will be called by autocomplete
        //      to obtain the current search string.
        init: function (parent, options) {
            this._super(parent);
            this.$input = parent.$el;
            this.get_search_string = options.get_search_string;
            this.current_result = null;
            this.searching = true;
            this.search_string = '';
            this.get_search_element = options.get_search_element;
            this.current_element = null
            this.selected_data = '';
            this.focus_data = '';
        },
        start: function () {
            var self = this;
            self.$el.parents().find('.oe_application_menu_placeholder a').on('click', function () {
                self.$el.parents().find('.o_sub_menu').css('display', 'block');
            });
            this.$input.on('focusout', function () {
                self.close()
            });
            this.$input.on('keyup', function (ev) {
                if (ev.which === $.ui.keyCode.RIGHT) {
                    self.searching = true;
                    ev.preventDefault();
                    return;
                }
                var search_string = self.get_search_string();
                if (self.search_string !== search_string) {
                    if (search_string.length) {
                        self.search_string = search_string;
                    } else {
                        self.close();
                    }
                }
            });
            this.$input.on('keypress', function (ev) {
                self.search_string = self.search_string + String.fromCharCode(ev.which);
                if (self.search_string.length) {
                    self.searching = true;
                    var search_string = self.search_string;
                } else {
                    self.close();
                }
            });
            this.$input.on('keydown', function (ev) {
                switch (ev.which) {
                    case $.ui.keyCode.ENTER:
                        // TAB and direction keys are handled at KeyDown because KeyUp
                        // is not guaranteed to fire.
                        // See e.g. https://github.com/aef-/jquery.masterblaster/issues/13
                    case $.ui.keyCode.TAB:
                        self.searching = false;
                        var current = self.current_result;
                        if (current && current.expand) {
                            ev.preventDefault();
                            ev.stopPropagation();
                            if (current.expanded) {
                                self.fold();
                            }
                            else {
                                self.expand();
                                self.searching = true;
                            }
                        }
                        else {
                            if (self.search_string.length) {
                                self.select_item(ev);
                            }
                        }
                        ev.preventDefault();
                        break;
                    case $.ui.keyCode.DOWN:
                        if (self.search_string) {
                            self.move('down');
                            self.searching = false;
                            ev.preventDefault();
                        }
                        break;
                    case $.ui.keyCode.UP:
                        if (self.search_string) {
                            self.move('up');
                            self.searching = false;
                            ev.preventDefault();
                        }
                        break;
                    case $.ui.keyCode.RIGHT:
                        self.searching = false;
                        var current = self.current_result;
                        if (current && current.expand && !current.expanded) {
                            self.expand();
                            self.searching = true;
                        }
                        ev.preventDefault();
                        break;
                    case $.ui.keyCode.ESCAPE:
                        self.close();
                        self.searching = false;
                        break;
                }
            });
        },
        search: function (query, models) {
            var self = this;
            self.current_search = query;
            self.render_search_results(models);
        },
        render_search_results: function (results) {
            var self = this;
            var $list = self.$('ul');
            $list.empty();
            var render_separator = false;
            var has_list = false
            $.each(results, function (key, val) {
                var result = {expand: true}
                result['model'] = [key, val]
                var $item = self.make_list_item(result).appendTo($list);
            });
            this.show();
        },
        make_list_item: function (result) {
            var self = this;
            var $li = $('<li>')
                    .hover(function () {
                        self.focus_element($li);
                    })
                    .mousedown(function (ev) {
                        self.searching = false;
                        var current = self.current_result;

                        if (current && current.expand) {
                            ev.preventDefault();
                            ev.stopPropagation();
                            if (current.expanded) {
                                self.fold();
                            }
                            else {
                                self.expand();
                            }
                        }
                        else {
                            if (self.search_string.length) {
                                self.select_item(ev);
                            }
                        }
                        ev.preventDefault();
                    })
                    .data('result', result);
            if (result.expand) {
                var $expand = $('<span class="oe-expand fa fa-chevron-right">').appendTo($li);
                result.expanded = false;
                $li.append($('<span>').html('Search <em>' + result.model[0] + '</em> for: <strong>' + self.search_string + '</strong>'));
            }
            if (result.indent) {
                if (result.label) {
                    $li.append($('<span>').html(' ' + result.label));
                }
                else {
                    var regex = RegExp(this.search_string, 'gi');
                    var replacement = '<strong>$&</strong>';
                    $li.append($('<strong>').html(' ' + result['display_name']));
                    for (var key in result) {
                        if ($.inArray(key, ['display_model', 'display_name', 'id', 'indent', 'model']) >= 0) {
                            continue;
                        }
                        $li.append($('<em>').html(' | ' + key));
                        $li.append($('<span>').html(': ' + String(result[key]).replace(regex, replacement)));
                    }
                }
                $li.addClass('oe-indent');
            }
            return $li;
        },
        expand: function () {
            var self = this;
            var current_result = this.current_result;
            return this._rpc({
                route: '/globalsearch/search_data',
                params: {
                    model: current_result['model'][1],
                    search_string: self.get_search_string()
                }
            }).then(function (results) {
                (results).reverse().forEach(function (result) {
                    if (Object.keys(result).length > 3 || result.label == '(no result)') {
                        result.display_model = current_result['model'][0]
                        result.indent = true;
                        var $li = self.make_list_item(result);
                        self.current_element.after($li);
                    }
                });
                current_result.expanded = true;
                self.current_element.find('span.oe-expand').removeClass('fa-chevron-right');
                self.current_element.find('span.oe-expand').addClass('fa-chevron-down');
            });
        },
        fold: function () {
            var $next = this.current_element.next();
            while ($next.hasClass('oe-indent')) {
                $next.remove();
                $next = this.current_element.next();
            }
            this.current_result.expanded = false;
            this.current_element.find('span.oe-expand').removeClass('fa-chevron-down');
            this.current_element.find('span.oe-expand').addClass('fa-chevron-right');
        },
        focus_element: function ($li) {
            this.$('li').removeClass('oe-selection-focus');
            $li.addClass('oe-selection-focus');
            this.current_result = $li.data('result');
            this.current_element = $li
            this.focus_data = $li.text();
        },
        remove_focus_element: function () {
            this.$('li').removeClass('oe-selection-focus');
            this.focus_data = ''
        },
        select_item: function (ev) {
            var self = this;
            if (self.current_result) {
                if (self.current_result.label == '(no result)') {
                    return true
                }
                if (self.current_result.expand) {
                    this.expand()
                }
                if (self.current_result.indent) {
                    var $li = self.$('li.oe-selection-focus')
                    self.selected_data = $li.data('result')
                    if (!_.isEmpty(self.selected_data)) {
                        self.$input.find('.global-search').val(self.selected_data['display_model'] + ':  ' + $.trim(this.focus_data.split('|')[0]))
                        self.close()
                        ev.preventDefault();
                        web_client.action_manager.action_stack = [];
                        web_client.action_manager.do_action({
                            'type': 'ir.actions.act_window',
                            'res_id': this.current_result['id'],
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': this.current_result['model'],
                            'target': 'current',
                            'views': [[false, 'form']],
                        }).then(function (result) {
                            self.$el.parents().find('.o_sub_menu').css('display', 'none');
                            rpc.query({
                                model: 'ir.model.data',
                                method: 'xmlid_to_res_id',
                                args: ['uppercrust_backend_theme.menu_global_search']
                            }).then(function (result) {
                                self.$el.parents().find('.oe_application_menu_placeholder a').parents().removeClass('active')
                                self.$el.parents().find('a[data-menu="' + String(result) + '"]').parent().addClass('active')
                            });
                        });
                    }
                }
            }
        },
        show: function () {
            this.$el.show();
        },
        close: function () {
            this.current_search = null;
            this.search_string = '';
            this.searching = true;
            this.$el.hide();
        },
        move: function (direction) {
            var $next;
            if (direction === 'down') {
                $next = this.$('li.oe-selection-focus').nextAll(':not(.oe-separator)').first();
                if (!$next.length) $next = this.$('li:first-child');
            } else {
                $next = this.$('li.oe-selection-focus').prevAll(':not(.oe-separator)').first();
                if (!$next.length) $next = this.$('li:not(.oe-separator)').last();
            }
            this.focus_element($next);
            $(".oe-global-autocomplete").scrollTop(0);//set to top
            if ($('li.oe-selection-focus').offset()) {
                $(".oe-global-autocomplete").scrollTop($('li.oe-selection-focus').offset().top - $(".oe-global-autocomplete").height());
            }
        },
        is_expandable: function () {
            return !!this.$('.oe-selection-focus .oe-expand').length;
        },
    });
});