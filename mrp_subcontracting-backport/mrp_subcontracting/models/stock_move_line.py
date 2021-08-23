# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    # in v13 addons/mrp/models/stock_move.py
    lot_produced_ids = fields.Many2many('stock.production.lot', string='Finished Lot/Serial Number', check_company=True)

    def create(self, values):
        records = super(StockMoveLine, self).create(values)
        records.filtered(lambda ml: ml.move_id.is_subcontract).move_id._check_overprocessed_subcontract_qty()
        return records

    def write(self, vals):
        # in v13 'mrp_subcontracting'
        res = super(StockMoveLine, self).write(vals)
        self.filtered(lambda ml: ml.move_id.is_subcontract).move_id._check_overprocessed_subcontract_qty()

        # in v13 addons/mrp/models/stock_move.py
        for move_line in self:
            if move_line.move_id.production_id and 'lot_id' in vals:
                move_line.production_id.move_raw_ids.mapped('move_line_ids')\
                    .filtered(lambda r: not r.done_move and move_line.lot_id in r.lot_produced_ids)\
                    .write({'lot_produced_ids': [(4, vals['lot_id'])]})
            production = move_line.move_id.production_id or move_line.move_id.raw_material_production_id
            if production and move_line.state == 'done' and any(field in vals for field in ('lot_id', 'location_id', 'qty_done')):
                move_line._log_message(production, move_line, 'mrp.track_production_move_template', vals)

        return res

    def _should_bypass_reservation(self, location):
        """ If the move line is subcontracted then ignore the reservation. """
        should_bypass_reservation = super(StockMoveLine, self)._should_bypass_reservation(location)
        if not should_bypass_reservation and self.move_id.is_subcontract:
            return True
        return should_bypass_reservation
