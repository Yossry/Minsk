odoo.define('odoo_marketplace.mp_backend_widgets', function (require) {
'use strict';
    var Followers = require('mail.Followers');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    Followers.include({
        _displayFollowers: function () {
            var self = this;
            var mp_hide_follows = false
            if(this.attrs.options.mp_hide_follows){
                mp_hide_follows = true
            }
            var isEditable = self.isEditable;

            // render the dropdown content
            var $followers_list = this.$('.o_followers_list').empty();
            if(!mp_hide_follows){
                $(QWeb.render('mail.Followers.add_more', {widget: this})).appendTo($followers_list);
            }
            var $follower_li;
            if(mp_hide_follows){
                self.isEditable = false
            }
            _.each(this.followers, function (record) {
                $follower_li = $(QWeb.render('mail.Followers.partner', {
                    'record': _.extend(record, {'avatar_url': '/web/image/' + record.res_model + '/' + record.res_id + '/image_small'}),
                    'widget': self})
                );
                $follower_li.appendTo($followers_list);

                // On mouse-enter it will show the edit_subtype pencil.
                if (record.is_editable) {
                    $follower_li.on('mouseenter mouseleave', function (e) {
                        $(e.currentTarget).find('.o_edit_subtype').toggleClass('d-none', e.type === 'mouseleave');
                    });
                }
            });
            if(mp_hide_follows){
                self.isEditable = isEditable
            }

            // clean and display title
            this.$('.o_followers_actions').show();
            this.$('.o_followers_title_box > button').prop('disabled', !$followers_list.children().length);
            this.$('.o_followers_count')
                .html(this.value.res_ids.length)
                .parent().attr('title', this._formatFollowers(this.value.res_ids.length));
        },
    });
});
