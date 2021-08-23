##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 25/mag/2016 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    info@omniasolutions.eu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
Created on 25/mag/2016

@author: mboscolo
"""

from odoo import models
from odoo import fields
from odoo import api
from odoo import _


class MrpBomLineTemplateCuttedParts(models.Model):
    _inherit = 'mrp.bom.line'
    x_length = fields.Float(compute='compute_x_length',
                            string=_("X Length"),
                            default=0.0)
    y_length = fields.Float(compute='compute_y_length',
                            string=_("Y Length"),
                            default=0.0)
    client_x_length = fields.Float('Cutted Qty', default=0)
    client_y_length = fields.Float('Cutted Qty', default=0)
    cutted_qty = fields.Float('Cutted Qty', default=0)
        
    @api.multi
    def compute_x_length(self):
        for bom_line_id in self:
            if bom_line_id.cutted_type == 'server':
                bom_line_id.x_length = self.computeXLenghtByProduct(bom_line_id.bom_id.product_id)
            elif bom_line_id.cutted_type == 'client':
                bom_line_id.x_length = bom_line_id.client_x_length

    @api.multi
    def compute_y_length(self):
        for bom_line_id in self:
            if bom_line_id.cutted_type == 'server':
                bom_line_id.y_length = self.computeYLenghtByProduct(bom_line_id.bom_id.product_id)
            elif bom_line_id.cutted_type == 'client':
                bom_line_id.y_length = bom_line_id.client_y_length

    @api.model
    def computeYLenghtByProduct(self, product_id):
        material_percentage = product_id.wastage_percent or 1
        material_added = product_id.material_added
        row_material_y_length = product_id.row_material_y_length
        y_raw_material_length = product_id.row_material.row_material_y_length
        new_qty = (row_material_y_length * material_percentage) + material_added
        return new_qty / (1 if y_raw_material_length == 0 else y_raw_material_length)
        
    @api.multi
    def computeXLenghtByProduct(self, product_id):
        material_percentage = product_id.wastage_percent or 1
        material_added = product_id.material_added
        row_material_x_length = product_id.row_material_x_length
        x_raw_material_length = product_id.row_material.row_material_x_length
        new_qty = (row_material_x_length * material_percentage) + material_added
        return new_qty / (1 if x_raw_material_length == 0 else x_raw_material_length)
    
    @api.multi
    def write(self, vals):
        res = super(MrpBomLineTemplateCuttedParts, self).write(vals)
        if not self.env.context.get('skip_cutted_recompute'):
            self.recomputeCuttedQty()
        return res
    
    @api.model
    def create(self, vals):
        res = super(MrpBomLineTemplateCuttedParts, self).create(vals)
        res.recomputeCuttedQty()
        return res

    @api.multi
    def recomputeCuttedQty(self):
        ctx = self.env.context.copy()
        ctx['skip_cutted_recompute'] = True
        for bom_line_id in self:
            bom_line_id.with_context(ctx).product_qty = bom_line_id.computeCuttedTotalQty()

    @api.multi
    def computeCuttedTotalQty(self):
        for bom_line_id in self:
            if bom_line_id.cutted_type in ('server', 'client'):
                if bom_line_id.x_length or bom_line_id.y_length:
                    x_length = bom_line_id.x_length or 1
                    y_length = bom_line_id.y_length or 1
                    ret = x_length * y_length
                    cutted_qty = bom_line_id.cutted_qty or 1
                    ret = ret * cutted_qty
                    return ret or 1
            return bom_line_id.product_qty

    def computeTotalQty(self, xLenght, yLenght, cutted_qty):
        ret = xLenght * yLenght
        cutted_qty = cutted_qty or 1
        ret = ret * cutted_qty
        return ret or 1
        
        
