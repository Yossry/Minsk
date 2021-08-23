# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import re
import math
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers import main as main_shop
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute


class KingfisherSliderSettings(http.Controller):

    @http.route(['/kingfisher/pro_get_options'], type='json', auth="public", website=True)
    def get_slider_options(self):
        slider_options = []
        option = request.env['product.category.slider.config'].sudo().search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/kingfisher/pro_get_dynamic_slider'], type='http', auth='public', website=True)
    def get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['product.category.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header
            }
            if slider_header.prod_cat_type == 'product':
                values.update(
                    {'slider_details': slider_header.collections_product})
            if slider_header.prod_cat_type == 'category':
                values.update(
                    {'slider_details': slider_header.collections_category})
            values.update({'slider_type': slider_header.prod_cat_type})
            return request.render("kingfisher.kingfisher_cat_slider_view", values)

    @http.route(['/kingfisher/pro_image_effect_config'], type='json', auth='public', website=True)
    def product_image_dynamic_slider(self, **post):
        slider_data = request.env['product.category.slider.config'].sudo().search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.prod_cat_type + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/kingfisher/blog_get_options'], type='json', auth="public", website=True)
    def king_blog_get_slider_options(self):
        slider_options = []
        option = request.env['blog.slider.config'].sudo().search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/kingfisher/blog_get_dynamic_slider'], type='http', auth='public', website=True)
    def king_blog_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }
            return request.render("kingfisher.kingfisher_blog_slider_view", values)

    @http.route(['/kingfisher/blog_image_effect_config'], type='json', auth='public', website=True)
    def king_blog_product_image_dynamic_slider(self, **post):
        slider_data = request.env['blog.slider.config'].sudo().search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.no_of_counts + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    # Multi image gallery
    @http.route(['/kingfisher/multi_image_effect_config'], type='json', auth="public", website=True)
    def get_multi_image_effect_config(self):

        cur_website = request.website
        values = {
            'no_extra_options': cur_website.no_extra_options,
            'theme_panel_position': cur_website.thumbnail_panel_position,
            'interval_play': cur_website.interval_play,
            'enable_disable_text': cur_website.enable_disable_text,
            'color_opt_thumbnail': cur_website.color_opt_thumbnail,
            'change_thumbnail_size': cur_website.change_thumbnail_size,
            'thumb_height': cur_website.thumb_height,
            'thumb_width': cur_website.thumb_width,
        }
        return values

    # For multi product slider
    @http.route(['/kingfisher/product_multi_get_options'], type='json', auth="public", website=True)
    def product_multi_get_slider_options(self):
        slider_options = []
        option = request.env['multi.slider.config'].sudo().search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/kingfisher/product_multi_get_dynamic_slider'], type='http', auth='public', website=True)
    def product_multi_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['multi.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header
            }
            return request.render("kingfisher.kingfisher_multi_cat_slider_view", values)

    @http.route(['/kingfisher/product_multi_image_effect_config'], type='json', auth='public', website=True)
    def product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['multi.slider.config'].sudo().search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.no_of_collection + '-' + str(slider_data.id),
            'counts': slider_data.no_of_collection,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values


class KingfisherTheme(WebsiteSale):

    @http.route(['/shop/pager_selection/<model("product.per.page.no"):pl_id>'], type='http', auth="public", website=True)
    def product_page_change(self, pl_id, **post):
        request.session['default_paging_no'] = pl_id.name
        main.PPG = pl_id.name
        return request.redirect('/shop' or request.httprequest.referrer)

    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category>/page/<int:page>',
                 '/shop/brands'],
                type='http',
                auth='public',
                website=True)
    def shop(self, page=0, category=None, brand=None, search='', ppg=False, **post):

        # odoo11
        # for displaying after whishlist or add to cart button n product_detail page
        if request.env.get('product.attribute.category') != None:
            compare_tmpl_obj = request.env.ref(
                'website_sale_comparison.product_add_to_compare')
            if compare_tmpl_obj and compare_tmpl_obj.priority != 20:
                compare_tmpl_obj.sudo().write({'priority': 20})

        if brand:
            req_ctx = request.context.copy()
            req_ctx.setdefault('brand_id', int(brand))
            request.context = req_ctx
        result = super(KingfisherTheme, self).shop(
            page=page, category=category, brand=brand, search=search, **post)
        sort_order = ""
        cat_id = []

        # For paging
        page_no = request.env['product.per.page.no'].sudo().search(
            [('set_default_check', '=', True)])
        if page_no:
            ppg = page_no.name
        else:
            ppg = main_shop.PPG

        # product template object
        product_obj = request.env['product.template']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [list(map(int, v.split("-")))
                         for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])
        domain = request.website.sale_product_domain()
        domain += self._get_search_domain(search, category, attrib_values)
        url = "/shop"
        keep = QueryURL('/shop', category=category and int(category), search=search,
                        attrib=attrib_list, order=post.get('order'))
        if post:
            request.session.update(post)

        if search:
            post["search"] = search

        if attrib_list:
            post['attrib'] = attrib_list

        prevurl = request.httprequest.referrer
        if prevurl:
            if not re.search('/shop', prevurl, re.IGNORECASE):
                request.session['tag'] = ""
                request.session['sort_id'] = ""
                request.session['sortid'] = ""
                request.session['pricerange'] = ""
                request.session['min1'] = ""
                request.session['max1'] = ""
                request.session['curr_category'] = ""

        session = request.session
        cate_for_price = None
        # for category filter
        if category:
            cate_for_price = int(category)
            category = request.env['product.public.category'].sudo().browse(
                int(category))
            url = "/shop/category/%s" % slug(category)

        if category != None:
            for ids in category:
                cat_id.append(ids.id)
            domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                       ('public_categ_ids.parent_id', 'in', cat_id)]

        # for tag filter
        if session.get('tag'):
            session_tag = session.get('tag')[0]
            tag = session_tag
            if tag:
                tag = request.env['biztech.product.tags'].sudo().browse(
                    int(tag))
                domain += [('biztech_tag_ids', '=', int(tag))]
                request.session["tag"] = [tag.id, tag.name]

        # For Product Sorting
        if session.get('sort_id'):
            session_sort = session.get('sort_id')
            sort = session_sort
            sort_field = request.env['biztech.product.sortby'].sudo().browse(
                int(sort))
            request.session['product_sort_name'] = sort_field.name
            order_field = sort_field.sort_on.name
            order_type = sort_field.sort_type
            sort_order = '%s %s' % (order_field, order_type)
            if post.get("sort_id"):
                request.session["sortid"] = [
                    sort, sort_order, sort_field.name, order_type]

        # For Price slider
        is_price_slider = request.env.ref(
            'kingfisher.kingfisher_slider_layout')
        if is_price_slider:

            is_discount_hide = True if request.website.get_current_pricelist(
            ).discount_policy == 'with_discount' else False

            product_slider_ids = []
            asc_product_slider_obj = product_obj.search(
                domain, limit=1, order='list_price')
            desc_product_slider_obj = product_obj.search(
                domain, limit=1, order='list_price desc')
            if asc_product_slider_obj:
                # product_slider_ids.append(asc_product_slider_obj.website_price)
                product_slider_ids.append(
                    asc_product_slider_obj.website_price if is_discount_hide else asc_product_slider_obj.list_price)
            if desc_product_slider_obj:
                # product_slider_ids.append(desc_product_slider_obj.website_price)
                product_slider_ids.append(
                    desc_product_slider_obj.website_price if is_discount_hide else desc_product_slider_obj.list_price)

            if product_slider_ids:
                if post.get("range1") or post.get("range2") or not post.get("range1") or not post.get("range2"):
                    range1 = min(product_slider_ids)
                    range2 = max(product_slider_ids)
                    result.qcontext['range1'] = math.floor(range1)
                    result.qcontext['range2'] = math.ceil(range2)

                    if request.session.get('pricerange'):
                        if cate_for_price and request.session.get('curr_category') and request.session.get('curr_category') != int(cate_for_price):
                            request.session["min1"] = math.floor(range1)
                            request.session["max1"] = math.ceil(range2)

                    if session.get("min1") and session["min1"]:
                        post["min1"] = session["min1"]
                    if session.get("max1") and session["max1"]:
                        post["max1"] = session["max1"]
                    if range1:
                        post["range1"] = range1
                    if range2:
                        post["range2"] = range2
                    if range1 == range2:
                        post['range1'] = 0.0

                if request.session.get('min1') or request.session.get('max1'):
                    if request.session.get('min1'):
                        if request.session['min1'] != None:
                            # domain += [('list_price', '>=', request.session.get('min1')), ('list_price', '<=', request.session.get('max1'))]
                            # ========== for hide list-website price diffrence ====================
                            if is_discount_hide:
                                price_product_list = []
                                product_withprice = product_obj.search(domain)
                                for prod_id in product_withprice:
                                    if prod_id.website_price >= float(request.session['min1']) and prod_id.website_price <= float(request.session['max1']):
                                        price_product_list.append(prod_id.id)

                                if price_product_list:
                                    domain += [('id', 'in',
                                                price_product_list)]
                                else:
                                    domain += [('id', 'in', [])]
                            else:
                                domain += [('list_price', '>=', request.session.get('min1')),
                                           ('list_price', '<=', request.session.get('max1'))]
# ==============================

                            request.session["pricerange"] = str(
                                request.session['min1'])+"-To-"+str(request.session['max1'])

                if session.get('min1') and session['min1']:
                    result.qcontext['min1'] = session["min1"]
                    result.qcontext['max1'] = session["max1"]

        if cate_for_price:
            request.session['curr_category'] = int(cate_for_price)

        if request.session.get('default_paging_no'):
            ppg = int(request.session.get('default_paging_no'))

        product_count = product_obj.search_count(domain)
        pager = request.website.pager(url=url, total=product_count,
                                      page=page, step=ppg, scope=7, url_args=post)
        products = product_obj.search(
            domain, limit=ppg, offset=pager['offset'], order=sort_order)

        result.qcontext.update({'product_count': product_count,
                                'products': products,
                                'category': category,
                                'pager': pager,
                                'keep': keep,
                                'search': search,
                                'bins': TableCompute().process(products, ppg)})

        result.qcontext['brand'] = brand
        result.qcontext['domain'] = domain
        result.qcontext['brand_obj'] = request.env[
            'product.brands'].sudo().search([('id', '=', brand)])

        return result

    # @http.route()
    # def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
    #     result = super(KingfisherTheme, self).cart_update_json(
    #         product_id, line_id, add_qty, set_qty, display)
    #     order = request.website.sale_get_order()
    #     result.update({'kingfisher.hover_total': request.env['ir.ui.view'].render_template("kingfisher.hover_total", {
    #         'website_sale_order': order})
    #     })
    #     return result

    @http.route(['/king_pro/get_brand_slider'], type='http', auth='public', website=True)
    def get_brand_slider(self, **post):
        keep = QueryURL('/king_pro/get_brand_slider', brand_id=[])

        value = {
            'website_brands': False,
            'brand_header': False,
            'keep': keep
        }

        if post.get('product_count'):
            brand_data = request.env['product.brands'].sudo().search(
                [], limit=int(post.get('product_count')))
            if brand_data:
                value['website_brands'] = brand_data

        if post.get('product_label'):
            value['brand_header'] = post.get('product_label')

        return request.render("kingfisher.kingfisher_brand_slider_view", value)

    @http.route(['/kingfisher/removeattribute'], type='json', auth='public', website=True)
    def remove_selected_attribute(self, **post):
        if post.get("attr_remove"):
            remove = post.get("attr_remove")
            if remove == "pricerange":
                del request.session['min1']
                del request.session['max1']
                request.session[remove] = ''
                return True
            elif remove == "sortid":
                request.session[remove] = ''
                request.session["sort_id"] = ''
                return True
            elif remove == "tag":
                request.session[remove] = ''
                return True
