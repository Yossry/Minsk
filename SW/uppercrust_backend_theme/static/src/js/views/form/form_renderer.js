// odoo Form view inherit for teb view change and form first panel create.
odoo.define('uppercrust_backend_theme.FormRenderer', function (require) {
    "use strict";

    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer');
    var FormController = require('web.FormController');
    var config = require('web.config');
    var BasicRenderer = require('web.BasicRenderer');
    var dom = require('web.dom');
    var Qweb = core.qweb;

    FormController.include({
        _doUpdateSidebar: function (mode) {
            if (mode === 'readonly' && this.sidebar.$el.hasClass('o_drw_in')) {
                $('body').find('.ad_rightbar').addClass('o_open_sidebar');
            } else {
                $('body').find('.ad_rightbar').removeClass('o_open_sidebar');
            }
        },
        _updateSidebar: function () {
            this._super.apply(this, arguments);
            if (this.sidebar) {
                this._doUpdateSidebar(this.mode);
                this.sidebar.do_toggle(this.mode === 'readonly');
            }
        },
    });

    FormRenderer.include({
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .o_notification_box .oe_field_translate': '_onTranslate',
            'click .oe_title, .o_inner_group': '_onClick',
        }),
        _renderTagSheet: function (node) {
            this.has_sheet = true;
            var $sheet = $('<div>').addClass('o_form_sheet');
            $sheet.append(_.map(node.children, this._renderNode.bind(this)));
            $sheet.children().not('.o_notebook').not('.o_chatter.oe_chatter').wrapAll($('<div/>', {class: 'o_cu_panel'}));
            return $sheet;
        },
        _renderTabHeader: function (page, page_id) {
            var $a = $('<a>', {
                disable_anchor: 'true',
                role: 'tab',
                text: page.attrs.string,
            }).click(function () {
                $(this).parent('li')
                    .toggleClass("ad_close");
            });
            return $('<li class="ad_close">').append($a);
        },
        _renderTagNotebook: function (node) {
            var self = this;
            var $headers = $('<ul class="panel-ul" role="tablist">');
            var autofocusTab = -1;
            // renderedTabs is used to aggregate the generated $headers and $pages
            // alongside their node, so that their modifiers can be registered once
            // all tabs have been rendered, to ensure that the first visible tab
            // is correctly activated
            var renderedTabs = _.map(node.children, function (child, index) {
                var pageID = _.uniqueId('notebook_page_');
                var $header = self._renderTabHeader(child, pageID);
                var $page = self._renderTabPage(child, pageID);
                $header.append($page);
                if (autofocusTab === -1 && child.attrs.autofocus === 'autofocus') {
                    autofocusTab = index;
                }
                self._handleAttributes($header, child);
                $headers.append($header);
                return {
                    $header: $header,
                    $page: $page,
                    node: child,
                };
            });
            if (renderedTabs.length) {
                var tabToFocus = renderedTabs[Math.max(0, autofocusTab)];
                tabToFocus.$header.addClass('active');
                tabToFocus.$page.addClass('active');
            }
            // register the modifiers for each tab
            _.each(renderedTabs, function (tab) {
                self._registerModifiers(tab.node, self.state, tab.$header, {
                    callback: function (element, modifiers) {
                        // if the active tab is invisible, activate the first visible tab instead
                        if (modifiers.invisible && element.$el.hasClass('active')) {
                            element.$el.removeClass('active');
                            tab.$page.removeClass('active');
                            var $firstVisibleTab = $headers.find('li:not(.o_invisible_modifier):first()');
                            $firstVisibleTab.addClass('active');
                        }
                    },
                });
            });
            var $notebook = $('<div class="o_notebook">')
                    .data('name', node.attrs.name || '_default_')
                    .append($headers);
            this._registerModifiers(node, this.state, $notebook);
            this._handleAttributes($notebook, node);
            return $notebook;
        },
        _updateView: function () {
            this._super.apply(this, arguments);
            var self = this;
            _.each(this.allFieldWidgets[this.state.id], function (widget) {
                var idForLabel = self.idsForLabels[widget.name];
                var $widgets = self.$('.o_field_widget[name=' + widget.name + ']');
                var $label = idForLabel ? self.$('label[for=' + idForLabel + ']') : $();
                $label = $label.eq($widgets.index(widget.$el));
                if (widget.field.help) {
                    $label.addClass('o_label_help');
                }
            });
        },
        _renderHeaderButtons: function (node) {
            if ((/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) || (config.device.size_class < config.device.SIZES.SM)) {
                var $buttonGroups = $();
                var children = _.filter(node.children, {tag: 'button'});
                var children_buttons = _.map(children, this._renderHeaderButton.bind(this));
                if (children_buttons.length) {
                    $buttonGroups = $(Qweb.render('ButtonGroup'));
                    _.each(children_buttons, function ($btn) {
                        $buttonGroups.find('.dropdown-menu').append($('<li>').append($btn));
                    });
                }
                return $buttonGroups;
            }
            else {
                var self = this;
                var $buttons = $('<div>', {class: 'o_statusbar_buttons'});
                _.each(node.children, function (child) {
                    if (child.tag === 'button') {
                        $buttons.append(self._renderHeaderButton(child));
                    }
                });
                return $buttons;
            }
        },
    });
});