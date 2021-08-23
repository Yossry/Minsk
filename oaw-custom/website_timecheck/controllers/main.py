# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):
    @http.route("/shop/all_products", type="http", auth="public", website=True)
    def shop_all_products(self):
        request.session.update(
            {
                "all_products": True,
                "new_arrival": False,
                "special_offer": False,
                "all_stock": True,
                "hk_stock": False,
                "oversea_stock": False,
            }
        )
        return request.redirect("/shop")

    @http.route("/shop/special_offer", type="http", auth="public", website=True)
    def shop_special_offer(self):
        request.session.update(
            {
                "all_products": False,
                "new_arrival": False,
                "special_offer": True,
                "all_stock": True,
                "hk_stock": False,
                "oversea_stock": False,
            }
        )
        return request.redirect("/shop")

    @http.route("/shop/new_arrival", type="http", auth="public", website=True)
    def shop_new_arrival(self):
        request.session.update(
            {
                "all_products": False,
                "new_arrival": True,
                "special_offer": False,
                "all_stock": True,
                "hk_stock": False,
                "oversea_stock": False,
            }
        )
        return request.redirect("/shop")

    @http.route("/shop/all_stock", type="http", auth="public", website=True)
    def shop_all_stock(self):
        request.session.update(
            {
                "all_products": False,
                "new_arrival": False,
                "special_offer": False,
                "all_stock": True,
                "hk_stock": False,
                "oversea_stock": False,
            }
        )
        return request.redirect("/shop")

    @http.route("/shop/hk_stock", type="http", auth="public", website=True)
    def shop_hk_stock(self):
        request.session.update(
            {
                "all_products": False,
                "new_arrival": False,
                "special_offer": False,
                "all_stock": False,
                "hk_stock": True,
                "oversea_stock": False,
            }
        )
        return request.redirect("/shop")

    @http.route("/shop/oversea_stock", type="http", auth="public", website=True)
    def shop_oversea_stock(self):
        request.session.update(
            {
                "all_products": False,
                "new_arrival": False,
                "special_offer": False,
                "all_stock": False,
                "hk_stock": False,
                "oversea_stock": True,
            }
        )
        return request.redirect("/shop")

    @http.route(
        "/cart/update_payment_delivery_info", type="http", auth="public", website=True
    )
    def update_payment_delivery_info(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/shop")
        vals = {}
        if post.get("payment_method", False):
            vals["payment_method"] = post["payment_method"]
        if post.get("payment_desc", False):
            vals["payment_desc"] = post["payment_desc"]
        if post.get("picking_date", False):
            vals["picking_date"] = post["picking_date"]
        if post.get("other_inquiry", False):
            vals["other_inquiry"] = post["other_inquiry"]
        order.sudo().write(vals)
        return request.redirect("/order/submit")

    @http.route(["/order/submit"], type="http", auth="public", website=True)
    def order_submit(self):
        sale_order_id = request.session.get("sale_order_id")
        request.session["sale_last_order_id"] = sale_order_id
        request.session["sale_order_id"] = None
        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            order.sudo().message_subscribe([order.partner_id.id])
            # order.sudo().message_unsubscribe(
            #     [request.website.user_id.partner_id.id])
        else:
            return request.redirect("/shop")
        return request.render("website_timecheck.confirmation", {"order": order})

    @http.route(
        [
            """/shop""",
            """/shop/page/<int:page>""",
            """/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>""",  # noqa
            """/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>""",  # noqa
        ],
        type="http",
        auth="public",
        website=True,
    )
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        if category:
            request.session.update(
                {
                    "all_products": True,
                    "new_arrival": False,
                    "special_offer": False,
                    "all_stock": True,
                    "hk_stock": False,
                    "oversea_stock": False,
                }
            )
        res = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        return res

    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type="http",
        auth="public",
        website=True,
    )
    def product(self, product, category="", search="", **kwargs):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        return super(WebsiteSale, self).product(
            product=product, category=category, search=search, **kwargs
        )

    @http.route(["/shop/cart"], type="http", auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive="", **post):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        return super(WebsiteSale, self).cart(
            access_token=access_token, revive=revive, **post
        )

    def check_timecheck_access(self):
        user = request.env["res.users"].sudo().browse(request.uid)
        if user.sudo().has_group("supplier_user_access.group_supplier"):
            base_url = request.env["ir.config_parameter"].get_param("web.base.url")
            redirect = base_url + "/web"
            return http.redirect_with_hash(redirect)
        return False

    def _get_search_order(self, post):
        # Overwrite by QTL
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        # return 'website_published desc,%s , id desc' % post.get('order', 'website_sequence desc') # noqa
        return (
            "website_published desc, partner_offer_checked desc,"
            "website_product_seq_date desc, id desc"
        )

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()

        # >>> QTL Modified
        # if search:
        #     for srch in search.split(" "):
        #         domain += [
        #             '|', '|', '|', ('name', 'ilike',
        #                             srch), ('description', 'ilike', srch),
        #             ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)] # noqa
        if search:
            condition_list = []
            operator_list = []
            for srch in search.split(","):
                condition_list += [
                    ("name", "ilike", srch),
                    ("description", "ilike", srch),
                    ("description_sale", "ilike", srch),
                    ("product_variant_ids.default_code", "ilike", srch),
                    ("public_categ_ids.name", "ilike", srch),
                ]
            # Add '|' to the operator_list, as the search conditions will be
            # joined with OR but not AND
            condition_list_length = len(condition_list)
            while condition_list_length - 1 > 0:
                operator_list += ["|"]
                condition_list_length -= 1
            domain += operator_list + condition_list
        # <<< QTL Modified

        if category:
            domain += [("public_categ_ids", "child_of", int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [("attribute_line_ids.value_ids", "in", ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [("attribute_line_ids.value_ids", "in", ids)]

        return domain


class Website(Website):
    @http.route("/", type="http", auth="public", website=True)
    def index(self, **kw):
        # << QTL Set the homepage according to the settings
        url = request.website.homepage_url or "/"
        return request.redirect(url)
        # homepage = request.website.homepage_id
        # if homepage and (homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/': # noqa
        #     return request.env['ir.http'].reroute(homepage.url)

        # website_page = request.env['ir.http']._serve_page()
        # if website_page:
        #     return website_page
        # else:
        #     top_menu = request.website.menu_id
        #     first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered( # noqa
        #         lambda menu: menu.is_visible)
        #     if first_menu and first_menu[0].url not in ('/', '', '#') and (not (first_menu[0].url.startswith(('/?', '/#', ' ')))): # noqa
        #         return request.redirect(first_menu[0].url)

        # raise request.not_found()

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params["login_success"]:
            if (
                request.env["res.users"]
                .browse(request.uid)
                .has_group("base.group_user")
            ):
                redirect = b"/web?" + request.httprequest.query_string
            else:
                redirect = "/shop"
            return http.redirect_with_hash(redirect)
        return response
