# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale
from odoo.http import request
from werkzeug.exceptions import NotFound

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class WebsiteSale(WebsiteSale):
    @http.route(
        [
            """/shop/<supplier_url>""",
            """/shop/<supplier_url>/page/<int:page>""",
            """/shop/<supplier_url>/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>""",  # noqa
            """/shop/<supplier_url>/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>""",  # noqa
        ],
        type="http",
        auth="public",
        website=True,
    )
    def supplier_shop(
        self, supplier_url, page=0, category=None, search="", ppg=False, **post
    ):

        supplier = request.env["res.partner"].search(
            [("website_url", "=", supplier_url)]
        )
        if not supplier:
            raise NotFound()
        else:
            supplier = supplier[0]

        if category:
            category = (
                request.env["product.public.category"]
                .sudo()
                .search([("id", "=", int(category))], limit=1)
            )
            if not category or not category.can_access_from_current_website():
                raise NotFound()

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        attrib_list = request.httprequest.args.getlist("attrib")
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_supplier_stock_search_domain(
            search, int(supplier), category, attrib_values
        )

        keep = QueryURL(
            "/shop/%s" % supplier_url,
            category=category and int(category),
            search=search,
            attrib=attrib_list,
            order=post.get("order"),
        )

        request.context = dict(request.context, partner=request.env.user.partner_id)

        url = "/shop/%s" % supplier_url
        if search:
            post["search"] = search
        if attrib_list:
            post["attrib"] = attrib_list

        SupplierStock = request.env["supplier.stock"].with_context(bin_size=True)

        search_categories = False
        search_product = SupplierStock.sudo().search(domain)
        categs = (
            SupplierStock.sudo()
            .search(self._get_supplier_stock_domain(int(supplier)))
            .mapped("product_id")
            .mapped("product_tmpl_id")
            .mapped("public_categ_ids")
        )

        parent_category_ids = []
        if category:
            url = "/shop/{}/category/{}".format(supplier_url, slug(category))
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = len(search_product)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post
        )
        products = SupplierStock.sudo().search(
            domain,
            limit=ppg,
            offset=pager["offset"],
            order=self._get_supplier_stock_search_order(post),
        )

        ProductAttribute = request.env["product.attribute"]
        if products:
            # get all products without limit
            attributes = ProductAttribute.search(
                [
                    ("attribute_line_ids.value_ids", "!=", False),
                    (
                        "attribute_line_ids.product_tmpl_id",
                        "in",
                        search_product.sudo()
                        .mapped("product_id")
                        .mapped("product_tmpl_id")
                        .ids,
                    ),
                ]
            )
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        request.session.update({"supplier": supplier_url})

        values = {
            "supplier_url": supplier_url,
            "search": search,
            "category": category,
            "attrib_values": attrib_values,
            "attrib_set": attrib_set,
            "pager": pager,
            "products": products,
            "search_count": product_count,  # common for all searchbox
            "bins": TableCompute().process(products, ppg),
            "rows": PPR,
            "categories": categs,
            "attributes": attributes,
            "compute_currency": request.env.user.company_id.currency_id,
            "keep": keep,
            "parent_category_ids": parent_category_ids,
            "search_categories_ids": search_categories and search_categories.ids,
        }
        if category:
            values["main_object"] = category
        return request.render("website_timecheck_supplier.products", values)

    @http.route(
        ['/shop/<supplier_url>/product/<model("supplier.stock"):product>'],
        type="http",
        auth="public",
        website=True,
    )
    def supplier_product(self, supplier_url, product, category="", search="", **kwargs):
        if (
            not product.mapped("product_id")
            .sudo()
            .mapped("product_tmpl_id")
            .can_access_from_current_website()
        ):
            raise NotFound()

        ProductCategory = request.env["product.public.category"]

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist("attrib")
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL(
            "/shop/%s" % supplier_url,
            category=category and category.id,
            search=search,
            attrib=attrib_list,
        )

        categs = ProductCategory.sudo().search([("parent_id", "=", False)])

        values = {
            "supplier_url": supplier_url,
            "search": search,
            "category": category,
            "attrib_values": attrib_values,
            "attrib_set": attrib_set,
            "keep": keep,
            "categories": categs,
            "main_object": product,
            "product": product,
        }
        return request.render("website_timecheck_supplier.product", values)

    @http.route("/supplier/all_products", type="http", auth="public", website=True)
    def supplier_all_products(self):
        request.session.update(
            {"supplier_new_arrival": False, "supplier_special_offer": False}
        )
        redirect = (
            "/shop/%s" % request.session.supplier
            if request.session.supplier
            else request.httprequest.headers["Referer"]
        )
        return request.redirect(redirect)

    @http.route("/supplier/special_offer", type="http", auth="public", website=True)
    def supplier_special_offer(self):
        request.session.update(
            {"supplier_new_arrival": False, "supplier_special_offer": True}
        )
        redirect = (
            "/shop/%s" % request.session.supplier
            if request.session.supplier
            else request.httprequest.headers["Referer"]
        )
        return request.redirect(redirect)

    @http.route("/supplier/new_arrival", type="http", auth="public", website=True)
    def supplier_new_arrival(self):
        request.session.update(
            {"supplier_new_arrival": True, "supplier_special_offer": False}
        )
        redirect = (
            "/shop/%s" % request.session.supplier
            if request.session.supplier
            else request.httprequest.headers["Referer"]
        )
        return request.redirect(redirect)

    def _get_supplier_stock_search_order(self, post):
        return ""

    def _get_supplier_stock_domain(self, supplier):
        return [("partner_id", "=", supplier)]

    def _get_supplier_stock_search_domain(
        self, search, supplier, category, attrib_values
    ):
        domain = self._get_supplier_stock_domain(supplier)

        if search:
            condition_list = []
            operator_list = []
            for srch in search.split(","):
                condition_list += [
                    ("product_id.name", "ilike", srch),
                    ("product_id.description", "ilike", srch),
                    ("product_id.description_sale", "ilike", srch),
                    ("product_id.default_code", "ilike", srch),
                ]
            # Add '|' to the operator_list, as the search conditions will be
            # joined with OR but not AND
            condition_list_length = len(condition_list)
            while condition_list_length - 1 > 0:
                operator_list += ["|"]
                condition_list_length -= 1
            domain += operator_list + condition_list

        if category:
            domain += [("product_id.public_categ_ids", "child_of", int(category))]

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
                    domain += [("product_id.attribute_line_ids.value_ids", "in", ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [("product_id.attribute_line_ids.value_ids", "in", ids)]

        if request.session.get("supplier_new_arrival"):
            domain += [("new_arrival", "=", True)]
        if request.session.get("supplier_special_offer"):
            domain += [("special_offer", ">", 0)]

        return domain

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
        # Update session
        request.session.update({"supplier": False})
        return super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
