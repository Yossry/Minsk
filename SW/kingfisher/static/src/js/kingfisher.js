odoo.define('kingfisher.kingfisher_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');

    // Dynamic cart update
    $(document).ready(function() {
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;
            var clickwatch = (function() {
                var timer = 0;
                return function(callback, ms) {
                    clearTimeout(timer);
                    timer = setTimeout(callback, ms);
                };
            })();

            $(oe_website_sale).on("change", ".oe_cart input.js_quantity[data-product-id]", function() {
                var $input = $(this);
                if ($input.data('update_change')) {
                    return;
                }
                var value = parseInt($input.val(), 10);
                var $dom = $(this).closest('tr');
                var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
                var line_id = parseInt($input.data('line-id'), 10);
                var product_id = parseInt($input.data('product-id'), 10);
                var product_ids = [product_id];
                clickwatch(function() {
                    $dom_optional.each(function() {
                        $(this).find('.js_quantity').text(value);
                        product_ids.push($(this).find('span[data-product-id]').data('product-id'));
                    });
                    $input.data('update_change', true);
                    ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'line_id': line_id,
                        'product_id': parseInt($input.data('product-id'), 10),
                        'set_qty': value
                    }).then(function(data) {
                        $input.data('update_change', false);
                        if (value !== parseInt($input.val(), 10)) {
                            $input.trigger('change');
                            return;
                        }

                        if(data.cart_quantity == undefined){
                            data['cart_quantity'] = 0; 
                        }
                        var $q1 = $(".my_cart_quantity");
                        $q1.fadeOut(500)

                        var startTime = new Date().getTime();
                        var my_hover_total = setInterval(function(){
                            if(new Date().getTime() - startTime > 1000){
                                clearInterval(my_hover_total);

                                $q1.html(data.cart_quantity).fadeIn(500);
                                return;
                            }
                            $("#king_hover_total").empty().html(data['kingfisher.hover_total']);
                        }, 100);

                        my_hover_total;
                    });
                }, 500);

            });

            $(oe_website_sale).on('click', '.o_wish_add', function() {
                setTimeout(function(){
                    window.location.reload();
                }, 800)
            });

            $(oe_website_sale).on('change', 'input.js_product_change', function () {
                var self = this;
                var $parent = $(this).closest('.js_product');
                update_gallery_product_variant_image(this, +$(this).val());
            });

            $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function(ev) {
                if (api != undefined){
                    var $ul = $(ev.target).closest('.js_add_cart_variants');
                    var $parent = $ul.closest('.js_product');
                    var variant_ids = $ul.data("attribute_value_ids");
                    var values = [];
                    if(_.isString(variant_ids)) {
                        variant_ids = JSON.parse(variant_ids.replace(/'/g, '"'));
                    }
                    var unchanged_values = $parent.find('div.oe_unchanged_value_ids').data('unchanged_value_ids') || [];
                    $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                        values.push(+$(this).val());
                    });
                    values =  values.concat(unchanged_values);

                    var product_id = false;
                    for (var k in variant_ids) {
                        if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                            product_id = variant_ids[k][0];
                            update_gallery_product_variant_image(this, product_id);
                            break;
                        }
                    }
                }
            });

        });

      $('#king_hover_total').on('click', '.js_remove_king_cart_product', function(e) {
            e.preventDefault();
            var $input = $(this).closest('li').find('.js_quantity')
            $(this).closest('li').find('.js_quantity').val(0).trigger('change');
            $(this).closest('li').fadeOut(700);

            var line_id = parseInt($input.data('line-id'), 10);
            ajax.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': line_id,
                'product_id': parseInt($input.data('product-id'), 10),
                'set_qty': 0
            }).then(function(data) {
                if(data.cart_quantity == undefined){
                    data['cart_quantity'] = 0; 
                }
                var $q1 = $(".my_cart_quantity");
                $q1.fadeOut(500)

                var startTime = new Date().getTime();
                var my_hover_total = setInterval(function(){
                    if(new Date().getTime() - startTime > 1000){
                        clearInterval(my_hover_total);

                        $q1.html(data.cart_quantity).fadeIn(500);
                        return;
                    }
                    $("#king_hover_total").empty().html(data['kingfisher.hover_total']);
                }, 100);

                my_hover_total;
            });
            if(location.pathname == '/shop/cart'){
                setTimeout(function(){
                    window.location.reload()
                }, 800);    
            }


        });

        // Multi image gallery
        var api;
        ajax.jsonRpc('/kingfisher/multi_image_effect_config', 'call', {})
            .done(function(res) {
                var dynamic_data = {}
                dynamic_data['gallery_images_preload_type'] = 'all'
                dynamic_data['slider_scale_mode'] = 'fit'
                dynamic_data['slider_enable_text_panel'] = false
                dynamic_data['gallery_skin'] = "alexis"
                dynamic_data['gallery_height'] = 800

                if (res.theme_panel_position != false) {
                    dynamic_data['theme_panel_position'] = res.theme_panel_position
                }

                if (res.interval_play != false) {
                    dynamic_data['gallery_play_interval'] = res.interval_play
                }

                if (res.color_opt_thumbnail != false && res.color_opt_thumbnail != 'default') {
                    dynamic_data['thumb_image_overlay_effect'] = true
                    if (res.color_opt_thumbnail == 'b_n_w') {}
                    if (res.color_opt_thumbnail == 'blur') {
                        dynamic_data['thumb_image_overlay_type'] = "blur"
                    }
                    if (res.color_opt_thumbnail == 'sepia') {
                        dynamic_data['thumb_image_overlay_type'] = "sepia"
                    }
                }

                if (res.enable_disable_text == true) {
                    dynamic_data['slider_enable_text_panel'] = true
                }

                if (res.change_thumbnail_size == true) {
                    dynamic_data['thumb_height'] = res.thumb_height
                    dynamic_data['thumb_width'] = res.thumb_width
                }

                if (res.no_extra_options == false) {
                    dynamic_data['slider_enable_arrows'] = false
                    dynamic_data['slider_enable_progress_indicator'] = false
                    dynamic_data['slider_enable_play_button'] = false
                    dynamic_data['slider_enable_fullscreen_button'] = false
                    dynamic_data['slider_enable_zoom_panel'] = false
                    dynamic_data['slider_enable_text_panel'] = false
                    dynamic_data['strippanel_enable_handle'] = false
                    dynamic_data['gridpanel_enable_handle'] = false
                    dynamic_data['theme_panel_position'] = 'bottom'
                    dynamic_data['thumb_image_overlay_effect'] = false
                }

                dynamic_data['thumb_image_overlay_effect'] = false

                api = $('#gallery').unitegallery(dynamic_data);
                api.on("item_change", function(num, data) {
                    if (data['index'] == 0) {
                        update_gallery_product_image();
                    }
                });

                if (api != undefined && $('#gallery').length != 0){
                    setTimeout(function(){
                        update_gallery_product_image()
                    }, 500);
                }
            });

        function update_gallery_product_image() {
            var $container = $('.oe_website_sale').find('.ug-slide-wrapper');
            var $img = $container.find('img');
            var $product_container = $('.oe_website_sale').find('.js_product').first();
            var p_id = parseInt($product_container.find('input.product_id').first().val());

            if (p_id > 0) {
                $img.each(function(e_img) {
                    if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                        if ($(this).attr("src").match('/flip_image') == null){
                            $(this).attr("src", "/web/image/product.product/" + p_id + "/image");
                        }
                    }
                });
            } else {
                var spare_link = api.getItem(0).urlThumb;
                $img.each(function(e_img) {
                    if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                        if ($(this).attr("src").match('/flip_image') == null){
                            $(this).attr("src", spare_link);
                        }
                    }
                });
            }
        }

        function update_gallery_product_variant_image(event_source, product_id) {
            var $imgs = $(event_source).closest('.oe_website_sale').find('.ug-slide-wrapper');
            var $img = $imgs.find('img');
            var total_img = api.getNumItems()
            if (total_img != undefined) {
                api.selectItem(0);
            }
            var $stay;
            $img.each(function(e) {
                if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                    if ($(this).attr("src").match('/flip_image') == null){
                        $(this).attr("src", "/web/image/product.product/" + product_id + "/image");

                        $stay = $(this).parent().parent();
                        $(this).css({
                            'width': 'initial',
                            'height': 'initial'
                        });
                        api.resetZoom();
                        api.zoomIn();
                    }
                }
            });
        }


        // Price slider code start
        var minval = $("input#m1").attr('value'),
            maxval = $('input#m2').attr('value'),
            minrange = $('input#ra1').attr('value'),
            maxrange = $('input#ra2').attr('value'),
            website_currency = $('input#king_pro_website_currency').attr('value');

        if (!minval) {
            minval = 0;
        }
        if (!maxval) {
            maxval = maxrange;
        }
        if (!minrange) {
            minrange = 0;

        }
        if (!maxrange) {
            maxrange = 2000;
        }

        $("div#priceslider").ionRangeSlider({
            keyboard: true,
            min: parseInt(minrange),
            max: parseInt(maxrange),
            type: 'double',
            from: minval,
            to: maxval,
            step: 1,
            prefix: website_currency,
            grid: true,
            onFinish: function(data) {
                $("input[name='min1']").attr('value', parseInt(data.from));
                $("input[name='max1']").attr('value', parseInt(data.to));
                $("div#priceslider").closest("form").submit();
            },
        });
        // Price slider code ends

        //attribute remove code
        $("a#clear").on('click', function() {
            var url = window.location.href.split("?");
            var lival = $(this).closest("label").attr('id');
            ajax.jsonRpc("/kingfisher/removeattribute", 'call', {
                'attr_remove': lival
            }).then(function(data) {
                if (data == true) {
                    window.location.href = url[0];
                }
            })
        });

    });
});
