# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class StockLocation(models.Model):
#     _inherit = "stock.location"
#     cedis_selection = fields.Selection([('occidente','Cedis Occidente'),('centro','Cedis Centro'),('sur','Cedis Sur')],string='Cedis')

class StockQuant(models.Model):
    _inherit = "stock.quant"

    code_product = fields.Char(related="product_id.default_code", string="Código del producto")

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    code_product_id = fields.Char(related="product_id.default_code", string="Código del producto")

class ProductInstallationType(models.Model):
    _name = 'product.installation.type'

    name = fields.Char(string="Tipo Instalacion")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_gdl = fields.Integer(string="Cedis occidente", compute="_compute")
    et_co = fields.Integer(string="En tránsito CO", compute="_compute")
    stock_cdmx = fields.Integer(string="Cedis centro", compute="_compute")
    et_cc = fields.Integer(string="En tránsito CC", compute="_compute")
    stock_mer = fields.Integer(string="Cedis sur", compute="_compute")
    et_cs = fields.Integer(string="En tránsito CS", compute="_compute")
    product_installation_type_id = fields.Many2one('product.installation.type', string='Tipo de instalacion')

    @api.one
    def _compute(self):

        id_stock_gdl = self.env['stock.location'].search([('name','=','GDL')],limit=1)
        id_stock_cdmx = self.env['stock.location'].search([('name','=','CDMX')],limit=1)
        id_stock_mer = self.env['stock.location'].search([('name','=','MER')],limit=1)

        product = self.env['product.product'].search([('product_tmpl_id','=',self.id)])

        product_sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_gdl.id)])
        if product_sq_gdl:
            self.stock_gdl += product_sq_gdl.quantity

        for x in id_stock_gdl.child_ids:
            product_sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
            if product_sq_gdl:
                self.stock_gdl += product_sq_gdl.quantity
            for y in x.child_ids:
                product_sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                if product_sq_gdl:
                    self.stock_gdl += product_sq_gdl.quantity

        product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_cdmx.id)])
        if product_sq_cdmx:
            self.stock_cdmx += product_sq_cdmx.quantity

        for x in id_stock_cdmx.child_ids:
            product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
            if product_sq_cdmx:
                self.stock_cdmx += product_sq_cdmx.quantity
            for y in x.child_ids:
                product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                if product_sq_cdmx:
                    self.stock_cdmx += product_sq_cdmx.quantity

        product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_mer.id)])
        if product_sq_mer:
            self.stock_mer += product_sq_mer.quantity

        for x in id_stock_mer.child_ids:
            product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
            if product_sq_mer:
                self.stock_mer += product_sq_mer.quantity
            for y in x.child_ids:
                product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                if product_sq_mer:
                    self.stock_mer += product_sq_mer.quantity

        product_reserved = self.env['stock.picking'].search([('state','in',['assigned']),('picking_type_code','=','outgoing')])
        product_reserved_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_reserved.ids)])

        for x in product_reserved_lines:
            for y in x.tiempo_entrega_tabla:
                if y.cedis_selection == 'occidente':
                    self.stock_gdl -= x.reserved_availability
                if y.cedis_selection == 'centro':
                    self.stock_cdmx -= x.reserved_availability
                if y.cedis_selection == 'sur':
                    self.stock_mer -= x.reserved_availability

        if self.stock_gdl < 0:
            self.stock_gdl = 0
        if self.stock_cdmx < 0:
            self.stock_cdmx = 0
        if self.stock_mer < 0:
            self.stock_mer = 0

        product_purchase= self.env['stock.picking'].search([('state','in',['confirmed','assigned']),('picking_type_code','=','incoming')])
        product_purchase_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_purchase.ids)])

        for x in product_purchase_lines:
            if x.picking_id.location_dest_id.location_id.name == 'GDL':
                self.et_co += x.product_uom_qty
            if x.picking_id.location_dest_id.location_id.name == 'CDMX':
                self.et_cc += x.product_uom_qty
            if x.picking_id.location_dest_id.location_id.name == 'MER':
                self.et_cs += x.product_uom_qty

        product_sale= self.env['stock.picking'].search([('state','in',['confirmed','assigned']),('picking_type_code','=','outgoing')])
        product_sale_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_sale.ids)])

        for x in product_sale_lines:
            for y in x.tiempo_entrega_tabla:
                if y.cedis_selection == 'occidente':
                    self.et_co -= (x.product_uom_qty - x.reserved_availability)
            for y in x.tiempo_entrega_tabla:
                if y.cedis_selection == 'centro':
                    self.et_cc -= (x.product_uom_qty - x.reserved_availability)
            for y in x.tiempo_entrega_tabla:
                if y.cedis_selection == 'sur':
                    self.et_cs -= (x.product_uom_qty - x.reserved_availability)

        if self.et_co < 0:
            self.et_co = 0
        if self.et_cc < 0:
            self.et_cc = 0
        if self.et_cs < 0:
            self.et_cs = 0

        # id_stock_gdl = self.env['stock.location'].search([('name','=','GDL')],limit=1)
        # product = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
        # cont = 0
        # socc = 0
        # scen = 0
        # ssur = 0
        # rsocc = 0
        # rscen = 0
        # rssur = 0
        # salidas = self.env['stock.picking'].search([('state','in',['confirmed']),('picking_type_code','=','outgoing'),('estado_reserva','in',['Anticipo','Autorizado_sin_pago','Pago_total_sin_documentos'])])
        # reservas = self.env['stock.picking'].search([('state','in',['assigned']),('picking_type_code','=','outgoing')])
        # sss = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',salidas.ids)])
        # rrr = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',reservas.ids)])
        # for x in sss:
        #     for y in x.tiempo_entrega_tabla:
        #         if y.cedis_selection == 'occidente':
        #             socc += x.product_qty
        #             print("TEST::: ",x.name,x.product_qty)
        #         if y.cedis_selection == 'centro':
        #             scen += x.product_qty
        #             print("TEST::: ",x.name,x.product_qty)
        #         if y.cedis_selection == 'sur':
        #             ssur += x.product_qty
        #             print("TEST::: ",x.name,x.product_qty)

        # for x in rrr:
        #     for y in x.tiempo_entrega_tabla:
        #         if y.cedis_selection == 'occidente':
        #             rsocc += x.product_qty
        #             print("R TEST::: ",x.name,x.product_qty)
        #         if y.cedis_selection == 'centro':
        #             rscen += x.product_qty
        #             print("R TEST::: ",x.name,x.product_qty)
        #         if y.cedis_selection == 'sur':
        #             rssur += x.product_qty
        #             print("R TEST::: ",x.name,x.product_qty)
        
        # #print(product.name,product.default_code)
        # p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_gdl.id)])
        # if p1:
        #     cont += p1.quantity

        # #print("LOCATION :: PATH :: ",id_stock_gdl.parent_path)
        # for x in id_stock_gdl.child_ids:
        #     p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
        #     if p1:
        #         #print(p1.quantity)
        #         cont += p1.quantity
        #     for y in x.child_ids:
        #         p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
        #         if p1:
        #             #print(p1.quantity)
        #             cont += p1.quantity
        # #print(product.name,cont)
        # self.stock_gdl = cont-p1.reserved_quantity-rsocc

        # id_stock_cdmx = self.env['stock.location'].search([('name','=','CDMX')], limit=1)
        # cdmxproduct=self.env['product.product'].search([('product_tmpl_id','=', self.id)])
        # cdmxcount = 0

        # p2 = self.env['stock.quant'].search([('product_id','=',cdmxproduct.id),('location_id','=',id_stock_cdmx.id)])
        # if p2:
        #     cdmxcount += p2.quantity

        # for cdmx in id_stock_cdmx.child_ids:
        #     p2 = self.env['stock.quant'].search([('product_id','=', cdmxproduct.id),('location_id','=',cdmx.id)])
        #     if p2:
        #         cdmxcount+=p2.quantity

        #     for cdy in cdmx.child_ids:
        #         p2=self.env['stock.quant'].search([('product_id','=',cdmxproduct.id),('location_id','=',cdy.id)])
        #         if p2:
        #             cdmxcount +=p2.quantity
        # self.stock_cdmx = cdmxcount-p2.reserved_quantity-rscen
        # #print(cdmxproduct.name, cdmxcount)

        # id_stock_mer = self.env['stock.location'].search([('name','=','MER')], limit=1)
        # merproduct=self.env['product.product'].search([('product_tmpl_id','=', self.id)])
        # mercount = 0

        # p3 = self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',id_stock_mer.id)])
        # if p3:
        #     merproduct+=p3.quantity

        # for merx in id_stock_mer.child_ids:
        #     p3= self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',merx.id)])
        #     if p3:
        #         mercount+=p3.quantity

        #     for mery in merx.child_ids:
        #         p3=self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',mery.id)])
        #         if p3:
        #             mercount+=p3.quantity
        # self.stock_mer=mercount-p3.reserved_quantity-rssur

        # id_stockw_gdl = self.env['stock.warehouse'].search([('code','=','GDL')],limit=1)
        # id_stockw_cdmx = self.env['stock.warehouse'].search([('code','=','CDMX')], limit=1)
        # id_stockw_mer = self.env['stock.warehouse'].search([('code','=','MER')], limit=1)

        # obj_transito = self.env['stock.move.line'].search([('code_product_id','=',self.default_code)])
        # id_vendor = self.env['stock.location'].search([('name','=','Vendors')], limit=1)

        # for x in obj_transito:
        #     if x.location_id.id == id_vendor.id:
        #         if id_stockw_gdl:
        #             if x.location_dest_id.id == id_stockw_gdl.lot_stock_id.id:
        #                 self.et_co = x.product_uom_qty - socc
        #         if id_stockw_cdmx:
        #             if x.location_dest_id.id == id_stockw_cdmx.lot_stock_id.id:
        #                 self.et_cc = x.product_uom_qty - scen
        #         if id_stockw_mer:
        #             if x.location_dest_id.id == id_stockw_mer.lot_stock_id.id:
        #                 self.et_cs = x.product_uom_qty - ssur


    