
odoo.define('wizard.planner', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var rpc = require('web.rpc');
var dom = require('web.dom');
var utils = require('web.utils');

//var Dialog = require('web.Dialog');
var session = require('web.session');

var QWeb = core.qweb;
var _t = core._t;

var MIN_PROGRESS = 7;

var Page = core.Class.extend({
    init: function (dom, page_index) {
        var $dom = $(dom);
        this.dom = dom;
        this.hide_from_menu = $dom.attr('hide-from-menu');
        this.hide_mark_as_done = $dom.attr('hide-mark-as-done');
        this.done = false;
        this.menu_item = null;
        this.title = $dom.find('[data-menutitle]').data('menutitle');

        var page_id = this.title.replace(/\s/g, '') + page_index;
        this.set_page_id(page_id);
    },
    set_page_id: function (id) {
        this.id = id;
        $(this.dom).attr('id', id);
    },
    toggle_done: function () {
        this.done = ! this.done;
    },
    get_category_name: function (category_selector) {
        var $page = $(this.dom);

        return $page.parents(category_selector).attr('menu-category-id');
    },
});

var WizardPlanner = Widget.extend({
	template: 'WizardPlanner',
	pages: [],
    menu_items: [],
    currently_shown_page: null,
    currently_active_menu_item: null,
    category_selector: 'div[menu-category-id]',    
    events: {
        'click li a[href^="#"]:not([data-toggle="collapse"])': 'change_page',
        'click a[href^="#show_enterprise"]': 'show_enterprise',
        'click button.mark_as_done': 'click_on_done',
        'click a.btn-next': 'change_to_next_page',
        'click .o_planner_close_block span': 'close_modal',
    },
      
	init: function(parent, planner) {
        this._super(parent);        
        this.planner = planner;
        this.cookie_name = this.planner.planner_application + '_last_page';
        this.pages = [];
        this.rec = this.planner.context.active_id;  //Added
        this.menu_items = [];
        this.planner_by_menu = {};  //Added
    },
    
    //Fetch the planner's rendered template, Changed model & args
    willStart: function() {       
        var def = rpc.query({
	    	model: 'wizard.planner',
	    	method: 'render',
	    	args: [1161,'planner_salary',this.rec],
	    	context: session.user_context,
        })
        .then((function(template) {
        	this.$template = $(template);
        }).bind(this));               
                
        return $.when(this._super.apply(this, arguments),def);        	
        
    }, 
    
    fetch_wizard_planner: function() {
        var self = this;
        var def = $.Deferred();
        if (!_.isEmpty(this.planner_by_menu)) {
            def.resolve(self.planner_by_menu);
        }else{
        	this._rpc({
            	model: 'wizard.planner',
            	method: 'search_read',
            	domain: [['rec_model', '=', 'hr.payroll.period'], ['rec_id', '=', this.rec]],
        	})
        	.then(function(res) {    		
		        _.each(res, function(planner){ 
		            self.planner_by_menu[planner.rec_id] = planner;
		            self.planner_by_menu[planner.rec_id].data = $.parseJSON(self.planner_by_menu[planner.rec_id].data) || {};
		            
		           
		            //alert(self.planner_by_menu.toSource());
		            /*
		            self.planner_by_menu[planner.menu_id[0]] = planner;
		            self.planner_by_menu[planner.menu_id[0]].data = $.parseJSON(planner.data) || {};
		            */
		        });
		        def.resolve(self.planner_by_menu);                        
        	}).fail(function() {def.reject();});
        	
        	
        }        
        return def;
    },
    
    start: function() {
        var self = this;
        
        /*
        self.planner = {
			tooltip_planner:"<p>Salary Processing: a step-by-step guide.\n        </p>", 
			write_uid:[1, "admin - Administrator"], 
			rec_model:"hr.payroll.period", 
			rec_id:1, 
			data:{}, 
			id:2, 
			display_name:"Salary Planner", 
			view_id:[1161, "salary_planner"], 
			planner_application:"planner_salary", 
			name:"Salary Planner", 
			progress:0, 
			active:true
		};				
		
        */
        
        
        var self = this;
        return this._super.apply(this, arguments).then(function() {            
            return self.fetch_wizard_planner();
        	}).then(function(wizards) { 
        		
            	self.planner_wizards = wizards;
        		self.planner = self.planner_wizards[self.rec];
        		self.cookie_name = self.planner.planner_application + '_last_page';
        		
		        //alert(self.planner_wizards[1].toSource());        
        		//return apps;
        	}).then(function() {
            self.$template.find('.o_planner_page').andSelf().filter('.o_planner_page').each(function(index, dom_page) {
                var page = new Page(dom_page, index);
                self.pages.push(page);
            });

            var $menu = self._render_menu();  // wil use self.$res
            self.$('.o_planner_menu ul').html($menu);
            self.menu_items = self.$('.o_planner_menu li');

            self.pages.forEach(function(page) {
                page.menu_item = self._find_menu_item_by_page_id(page.id);
            });
            self.$el.find('.o_planner_content_wrapper').append(self.$template);

            // update the planner_data with the new inputs of the view
            var actual_vals = self._get_values();
            self.planner.data = _.defaults(self.planner.data, actual_vals);
            // set the default value
            self._set_values(self.planner.data);
            // show last opened page
            self._show_last_open_page();
            self.prepare_planner_event();
        });
    },
    
    /*** This method should be overridden in other planners to bind their custom events once the view is loaded. */
    prepare_planner_event: function() {
        var self = this;
        this.on('change:progress', this, function() {
            self.trigger('planner_progress_changed', self.get('progress'));
        });
        this.on('planner_progress_changed', this, this.update_ui_progress_bar);
        // set progress to trigger initial UI update
        var initial_progress = false;
        if (!this.planner.progress) {
            var total_pages = 0;
            this.pages.forEach(function(page) {
                if (! page.hide_mark_as_done) {
                    total_pages++;
                }
            });
            initial_progress = parseInt(( 1 / (total_pages + 1)) * 100, 10);
        }
        this.set('progress', initial_progress || this.planner.progress);
    },
    
    _render_done_page: function (page) {
        var mark_as_done_button = this.$('.mark_as_done')
        var mark_as_done_li = mark_as_done_button.find('i');
        var next_button = this.$('a.btn-next');
        var active_menu = $(page.menu_item).find('span');
        if (page.done) {
            active_menu.addClass('fa-check');
            mark_as_done_button.removeClass('btn-primary');
            mark_as_done_li.removeClass('fa-square-o');
            mark_as_done_button.addClass('btn-default');
            mark_as_done_li.addClass('fa-check-square-o');
            next_button.removeClass('btn-default');
            next_button.addClass('btn-primary');

            // page checked animation
            $(page.dom).addClass('marked');
            setTimeout(function() {
                $(page.dom).removeClass('marked');
            }, 1000);
        } else {
            active_menu.removeClass('fa-check');
            mark_as_done_button.removeClass('btn-default');
            mark_as_done_li.removeClass('fa-check-square-o');
            mark_as_done_button.addClass('btn-primary');
            mark_as_done_li.addClass('fa-square-o');
            next_button.removeClass('btn-primary');
            next_button.addClass('btn-default');
        }
        if (page.hide_mark_as_done) {
            next_button.removeClass('btn-default').addClass('btn-primary');
        }
    },
    
    _show_last_open_page: function () {
        //debugger;
        var last_open_page = utils.get_cookie(this.cookie_name);

        if (! last_open_page) {
            last_open_page = this.planner.data.last_open_page || false;
        }

        if (last_open_page && this._find_page_by_id(last_open_page)) {
            this._display_page(last_open_page);
        } else {
            this._display_page(this.pages[0].id);
        }
    },
    
    update_ui_progress_bar: function(percent) {
        this.$(".progress-bar").css('width', percent+"%");
        this.$(".o_progress_text").text(percent+"%");
    },
    
    _create_menu_item: function(page, menu_items, menu_item_page_map) {
        var $page = $(page.dom);
        var $menu_item_element = $page.find('h1[data-menutitle]');
        var menu_title = $menu_item_element.data('menutitle') || $menu_item_element.text();

		//alert(menu_title);
        menu_items.push(menu_title);
        menu_item_page_map[menu_title] = page.id;
    },
    
    _render_menu: function() {
        var self = this;
        var orphan_pages = [];
        var menu_categories = [];
        var menu_item_page_map = {};

        // pages with no category
        self.pages.forEach(function(page) {            
            if (! page.hide_from_menu && ! page.get_category_name(self.category_selector)) {                
                self._create_menu_item(page, orphan_pages, menu_item_page_map);
            }
        });

        // pages with a category
        self.$template.filter(self.category_selector).each(function(index, menu_category) {
            var $menu_category = $(menu_category);
            var menu_category_item = {
                name: $menu_category.attr('menu-category-id'),
                classes: $menu_category.attr('menu-classes'),
                menu_items: [],
            };

            self.pages.forEach(function(page) {
                if (! page.hide_from_menu && page.get_category_name(self.category_selector) === menu_category_item.name) {
                    self._create_menu_item(page, menu_category_item.menu_items, menu_item_page_map);
                }
            });

            menu_categories.push(menu_category_item);

            // remove the branding used to separate the pages
            self.$template = self.$template.not($menu_category);
            self.$template = self.$template.add($menu_category.contents());
        });

        var menu = QWeb.render('WizardPlannerMenu', {
            'orphan_pages': orphan_pages,
            'menu_categories': menu_categories,
            'menu_item_page_map': menu_item_page_map
        });

        return menu;
    },
    
    get_next_page_id: function() {
        var self = this;
        var current_page_found = false;
        var next_page_id = null;
        this.pages.every(function(page) {
            if (current_page_found) {
                next_page_id = page.id;
                return false;
            }

            if (page.id === self.currently_shown_page.id) {
                current_page_found = true;
            }

            return true;
        });

        return next_page_id;
    },
    
    change_to_next_page: function(ev) {
        var next_page_id = this.get_next_page_id();

        ev.preventDefault();

        if (next_page_id) {
            this._display_page(next_page_id);
        }
    },
    
    change_page: function(ev) {
        ev.preventDefault();
        var page_id = $(ev.currentTarget).attr('href').replace('#', '');
        this._display_page(page_id);
    },
    
    _find_menu_item_by_page_id: function (page_id) {
        var result = _.find(this.menu_items, function (menu_item) {
            var $menu_item = $(menu_item);
            return $($menu_item.find('a')).attr('href') === '#' + page_id;
        });

        return result;
    },
    
    _find_page_by_id: function (id) {
        var result = _.find(this.pages, function (page) {
            return page.id === id;
        });

        return result;
    },
    
    _display_page: function(page_id) {
        var self = this;
        //debugger;
        var mark_as_done_button = this.$('button.mark_as_done');
        var next_button = this.$('a.btn-next');
        var page = this._find_page_by_id(page_id);
        if (this.currently_active_menu_item) {
            $(this.currently_active_menu_item).removeClass('active');
        }

        var menu_item = this._find_menu_item_by_page_id(page_id);
        $(menu_item).addClass('active');
        this.currently_active_menu_item = menu_item;

        if (this.currently_shown_page) {
            $(this.currently_shown_page.dom).removeClass('show');
        }

        $(page.dom).addClass('show');
        this.currently_shown_page = page;

        if (! this.get_next_page_id()) {
            next_button.hide();
        } else {
            next_button.show();
        }

        if (page.hide_mark_as_done) {
            mark_as_done_button.hide();
        } else {
            mark_as_done_button.show();
        }

        this._render_done_page(this.currently_shown_page);

        this.planner.data.last_open_page = page_id;
        utils.set_cookie(this.cookie_name, page_id, 8*60*60); // create cookie for 8h
        this.$(".modal-body").scrollTop("0");

        this.$('textarea').each(function () {
            dom_utils.autoresize($(this), {parent: self});
        });

        this.$('.o_currently_shown_page').text(this.currently_shown_page.title);
    },
    
    // planner data functions
    _get_values: function(page){
        // if no page_id, take the complete planner
        var base_elem = page ? $(page.dom) : this.$(".o_planner_page");
        var values = {};
        // get the selector for all the input and mark_button
        // only INPUT (select, textearea, input, checkbox and radio), and BUTTON (.mark_button#) are observed
        var inputs = base_elem.find("textarea[id^='input_element'], input[id^='input_element'], select[id^='input_element'], button[id^='mark_button']");
        _.each(inputs, function(elem){
            var $elem = $(elem);
            var tid = $elem.attr('id');
            if ($elem.prop("tagName") === 'BUTTON'){
                if($elem.hasClass('fa-check-square-o')){
                    values[tid] = 'marked';
                }else{
                    values[tid] = '';
                }
            }
            if ($elem.prop("tagName") === 'INPUT' || $elem.prop("tagName") === 'TEXTAREA'){
                var ttype = $elem.attr('type');
                if (ttype === 'checkbox' || ttype === 'radio'){
                    values[tid] = '';
                    if ($elem.is(':checked')){
                        values[tid] = 'checked';
                    }
                }else{
                    values[tid] = $elem.val();
                }
            }
        });

        this.pages.forEach(function(page) {
            values[page.id] = page.done;
        });
        return values;
    },
    _set_values: function(values){
        var self = this;
        _.each(values, function(val, id){
            var $elem = self.$('[id="'+id+'"]');
            if ($elem.prop("tagName") === 'BUTTON'){
                if(val === 'marked'){
                    $elem.addClass('fa-check-square-o btn-default').removeClass('fa-square-o btn-primary');
                    self.$("li a[href=#"+$elem.data('pageid')+"] span").addClass('fa-check');
                }
            }
            if ($elem.prop("tagName") === 'INPUT' || $elem.prop("tagName") === 'TEXTAREA'){
                var ttype = $elem.attr("type");
                if (ttype  === 'checkbox' || ttype === 'radio'){
                    if (val === 'checked') {
                       $elem.attr('checked', 'checked');
                    }
                }else{
                    $elem.val(val);
                }
            }
        });

        this.pages.forEach(function(page) {
            page.done = values[page.id];
            self._render_done_page(page);
        });
    },
    
    update_planner: function(){
        // update the planner.data with the inputs
        var vals = this._get_values(this.currently_shown_page);
        this.planner.data = _.extend(this.planner.data, vals);

        // re compute the progress percentage
        var total_pages = 0;
        var done_pages = 0;

        this.pages.forEach(function(page) {
            if (! page.hide_mark_as_done) {
                total_pages++;
            }
            if (page.done) {
                done_pages++;
            }
        });
        var percent = parseInt(( (done_pages + 1) / (total_pages + 1)) * 100, 10);
        this.set('progress', percent);

        this.planner.progress = percent;
        // save data and progress in database
        this._save_planner_data();
    },
    
    _save_planner_data: function() {
        return rpc.query({
	    	model: 'wizard.planner',
	    	method: 'write',
	    	args: [this.planner.id, {'data': JSON.stringify(this.planner.data), 'progress': this.planner.progress}],
	    	context: session.user_context,
        });
    },
    
    click_on_done: function(ev) {
        ev.preventDefault();
        this.currently_shown_page.toggle_done();
        this._render_done_page(this.currently_shown_page);
        this.update_planner();
    },
    
    
    
});

core.action_registry.add('wizard_planner_main', WizardPlanner);

return {
    WizardPlanner: WizardPlanner,   
};

//return WizardPlanner;

});
