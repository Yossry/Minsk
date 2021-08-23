odoo.define('kingfisher_structure.rating_state_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;

    ajax.loadXML('/website_rating/static/src/xml/website_mail.xml', qweb);
    var PortalChatter = require('portal.chatter').PortalChatter;
 
    PortalChatter.include({
        start: function(){
            var res = this._super.apply(this);
            var rating_val = this.options['rating_val'];
            var only_rating = this.options['only_rating'];

            if (only_rating == 1){
                if (rating_val && rating_val < 6){
                    this.$el.closest('.o_portal_chatter').empty().html(qweb.render("website_rating.rating_stars_static", {'val': rating_val}));
                }
                else if(rating_val == 6){
                    this.$el.closest('.o_portal_chatter').empty().html(qweb.render("website_rating.rating_stars_static", {'val': 0.0}));
                }
            }
            return res
        }
    });
});

