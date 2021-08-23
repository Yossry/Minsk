# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero, float_round, float_compare
from datetime import datetime

class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    subcontract_move_id = fields.Many2one('stock.move', 'stock move from the subcontract picking', check_company=True)

    # in v13 mrp_product_produce.py :
    raw_workorder_line_ids = fields.One2many('mrp.product.produce.line',
        'raw_product_produce_id', string='Components')
    finished_workorder_line_ids = fields.One2many('mrp.product.produce.line',
        'finished_product_produce_id', string='By-products')

    # in v13 mrp_abstract_workorder.py :
    consumption = fields.Selection([
        ('strict', 'Strict'),
        ('flexible', 'Flexible')],
        # required=True, # no need to be required=True in v12
    )
    finished_lot_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)

    def continue_production(self):
        action = super(MrpProductProduce, self).continue_production()
        action['context'] = dict(action['context'], default_subcontract_move_id=self.subcontract_move_id.id)
        return action

    def _generate_produce_lines(self):
        """ When the wizard is called in backend, the onchange that create the
        produce lines is not trigger. This method generate them and is used with
        _record_production to appropriately set the lot_produced_id and
        appropriately create raw stock move lines.
        """
        self.ensure_one()
        moves = (self.production_id.move_raw_ids | self.production_id.move_finished_ids).filtered(
            lambda move: move.state not in ('done', 'cancel')
        )
        for move in moves:
            qty_to_consume = self._prepare_component_quantity(move, self.product_qty) # qty_producing in v13
            line_values = self._generate_lines_values(move, qty_to_consume)
            self.env['mrp.product.produce.line'].create(line_values)

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _update_finished_move(self):
        """ Update the finished move & move lines in order to set the finished
        product lot on it as well as the produced quantity. This method get the
        information either from the last workorder or from the Produce wizard."""
        production_move = self.production_id.move_finished_ids.filtered(
            lambda move: move.product_id == self.product_id and
            move.state not in ('done', 'cancel')
        )
        if production_move and production_move.product_id.tracking != 'none':
            if not self.finished_lot_id:
                raise UserError(_('You need to provide a lot for the finished product.'))
            move_line = production_move.move_line_ids.filtered(
                lambda line: line.lot_id.id == self.finished_lot_id.id
            )
            if move_line:
                if self.product_id.tracking == 'serial':
                    raise UserError(_('You cannot produce the same serial number twice.'))
                move_line.product_uom_qty += self.product_qty # qty_producing in v13
                move_line.qty_done += self.product_qty
            else:
                location_dest_id = production_move.location_dest_id._get_putaway_strategy(self.product_id).id or production_move.location_dest_id.id
                move_line.create({
                    'move_id': production_move.id,
                    'product_id': production_move.product_id.id,
                    'lot_id': self.finished_lot_id.id,
                    'product_uom_qty': self.product_qty,
                    'product_uom_id': self.product_uom_id.id,
                    'qty_done': self.product_qty,
                    'location_id': production_move.location_id.id,
                    'location_dest_id': location_dest_id,
                })
        else:
            rounding = production_move.product_uom.rounding
            production_move._set_quantity_done(
                float_round(self.product_qty, precision_rounding=rounding)
            )

        # Part of the '_update_finished_move method' in v13 'mrp_subcontracting'
        """ After producing, set the move line on the subcontract picking. """
        if self.subcontract_move_id:
            self.env['stock.move.line'].create({
                'move_id': self.subcontract_move_id.id,
                'picking_id': self.subcontract_move_id.picking_id.id,
                'product_id': self.product_id.id,
                'location_id': self.subcontract_move_id.location_id.id,
                'location_dest_id': self.subcontract_move_id.location_dest_id.id,
                'product_uom_qty': 0,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': self.product_qty, # qty_producing in v13
                'lot_id': self.finished_lot_id and self.finished_lot_id.id,
            })
            if not self._get_todo(self.production_id):
                ml_reserved = self.subcontract_move_id.move_line_ids.filtered(lambda ml:
                    float_is_zero(ml.qty_done, precision_rounding=ml.product_uom_id.rounding) and
                    not float_is_zero(ml.product_uom_qty, precision_rounding=ml.product_uom_id.rounding))
                ml_reserved.unlink()
                for ml in self.subcontract_move_id.move_line_ids:
                    ml.product_uom_qty = ml.qty_done
                self.subcontract_move_id._recompute_state()

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _update_moves(self):
        """ Once the production is done. Modify the workorder lines into
        stock move line with the registered lot and quantity done.
        """
        # Before writting produce quantities, we ensure they respect the bom strictness
        self._strict_consumption_check()
        vals_list = []
        workorder_lines_to_process = self._workorder_line_ids().filtered(lambda line: line.product_id != self.product_id and line.qty_done > 0)
        for line in workorder_lines_to_process:
            line._update_move_lines()
            if float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding) > 0:
                vals_list += line._create_extra_move_lines()

        self._workorder_line_ids().filtered(lambda line: line.product_id != self.product_id).unlink()
        self.env['stock.move.line'].create(vals_list)

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _strict_consumption_check(self):
        if self.consumption == 'strict':
            for move in self.production_id.move_raw_ids:
                lines = self._workorder_line_ids().filtered(lambda l: l.move_id == move)
                qty_done = 0.0
                qty_to_consume = 0.0
                for line in lines:
                    qty_done += line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                    qty_to_consume += line.product_uom_id._compute_quantity(line.qty_to_consume, line.product_id.uom_id)
                rounding = self.product_uom_id.rounding
                if float_compare(qty_done, qty_to_consume, precision_rounding=rounding) != 0:
                    raise UserError(_('You should consume the quantity of %s defined in the BoM. If you want to consume more or less components, change the consumption setting on the BoM.') % lines[0].product_id.name)


    # method in v13 'mrp_abstract_workorder' but not in v12
    @api.model
    def _prepare_component_quantity(self, move, product_qty):
        """ helper that computes quantity to consume (or to create in case of byproduct)
        depending on the quantity producing and the move's unit factor"""
        if move.product_id.tracking == 'serial':
            uom = move.product_id.uom_id
        else:
            uom = move.product_uom
        return move.product_uom._compute_quantity(
            product_qty * move.unit_factor,
            uom,
            round=False
        )

    # method in v13 'mrp_abstract_workorder' but not in v12
    @api.model
    def _generate_lines_values(self, move, qty_to_consume):
        """ Create workorder line. First generate line based on the reservation,
        in order to prefill reserved quantity, lot and serial number.
        If the quantity to consume is greater than the reservation quantity then
        create line with the correct quantity to consume but without lot or
        serial number.
        """
        lines = []
        is_tracked = move.product_id.tracking == 'serial'
        if move in self.production_id.move_raw_ids: # self.move_raw_ids._origin in v13
            # Get the inverse_name (many2one on line) of raw_workorder_line_ids
            initial_line_values = {self.raw_workorder_line_ids._get_raw_workorder_inverse_name(): self.id}
        else:
            # Get the inverse_name (many2one on line) of finished_workorder_line_ids
            initial_line_values = {self.finished_workorder_line_ids._get_finished_workoder_inverse_name(): self.id}
        for move_line in move.move_line_ids:
            line = dict(initial_line_values)
            if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) <= 0:
                break
            # move line already 'used' in workorder (from its lot for instance)
            if move_line.lot_produced_ids or float_compare(move_line.product_uom_qty, move_line.qty_done, precision_rounding=move.product_uom.rounding) <= 0:
                continue
            # search wo line on which the lot is not fully consumed or other reserved lot
            linked_wo_line = self._workorder_line_ids().filtered(
                lambda line: line.move_id == move and
                line.lot_id == move_line.lot_id
            )
            if linked_wo_line:
                if float_compare(sum(linked_wo_line.mapped('qty_to_consume')), move_line.product_uom_qty - move_line.qty_done, precision_rounding=move.product_uom.rounding) < 0:
                    to_consume_in_line = min(qty_to_consume, move_line.product_uom_qty - move_line.qty_done - sum(linked_wo_line.mapped('qty_to_consume')))
                else:
                    continue
            else:
                to_consume_in_line = min(qty_to_consume, move_line.product_uom_qty - move_line.qty_done)
            line.update({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_id': is_tracked and move.product_id.uom_id.id or move.product_uom.id,
                'qty_to_consume': to_consume_in_line,
                'qty_reserved': to_consume_in_line,
                'lot_id': move_line.lot_id.id,
                'qty_done': to_consume_in_line,
            })
            lines.append(line)
            qty_to_consume -= to_consume_in_line
        # The move has not reserved the whole quantity so we create new wo lines
        if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
            line = dict(initial_line_values)
            if move.product_id.tracking == 'serial':
                while float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    line.update({
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_id.uom_id.id,
                        'qty_to_consume': 1,
                        'qty_done': 1,
                    })
                    lines.append(line)
                    qty_to_consume -= 1
            else:
                line.update({
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'qty_to_consume': qty_to_consume,
                    'qty_done': qty_to_consume,
                })
                lines.append(line)
        return lines

    def _workorder_line_ids(self):
        self.ensure_one()
        return self.raw_workorder_line_ids | self.finished_workorder_line_ids

    # method in v13 'mrp_product_produce' but not in v12
    def _record_production(self):
        # Check all the product_produce line have a move id (the user can add product
        # to consume directly in the wizard)
        for line in self._workorder_line_ids():
            if not line.move_id:
                # Find move_id that would match
                if line.raw_product_produce_id:
                    moves = self.production_id.move_raw_ids
                else:
                    moves = self.production_id.move_finished_ids
                move_id = moves.filtered(lambda m: m.product_id == line.product_id and m.state not in ('done', 'cancel'))
                if not move_id:
                    # create a move to assign it to the line
                    if line.raw_product_produce_id:
                        values = {
                            'name': self.production_id.name,
                            'reference': self.production_id.name,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'location_id': self.production_id.location_src_id.id,
                            'location_dest_id': line.product_id.property_stock_production.id,
                            'raw_material_production_id': self.production_id.id,
                            'group_id': self.production_id.procurement_group_id.id,
                            'origin': self.production_id.name,
                            'state': 'confirmed',
                            'company_id': self.production_id.company_id.id,
                        }
                    else:
                        values = self.production_id._get_finished_move_value(line.product_id.id, 0, line.product_uom_id.id)
                    move_id = self.env['stock.move'].create(values)
                line.move_id = move_id.id

        # because of an ORM limitation (fields on transient models are not
        # recomputed by updates in non-transient models), the related fields on
        # this model are not recomputed by the creations above
        # self.invalidate_cache(['move_raw_ids', 'move_finished_ids']) # No move_raw_ids and move_finished_ids

        # Save product produce lines data into stock moves/move lines
        quantity = self.product_qty # qty_producing in v13
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified.") % self.product_id.display_name)
        self._update_finished_move()
        self._update_moves()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'date_start': datetime.now(),
            })

class MrpProductProduceLine(models.TransientModel):
    _inherit = 'mrp.product.produce.line'

    raw_product_produce_id = fields.Many2one('mrp.product.produce', 'Component in Produce wizard')
    finished_product_produce_id = fields.Many2one('mrp.product.produce', 'Finished Product in Produce wizard')

    @api.model
    def _get_raw_workorder_inverse_name(self):
        return 'raw_product_produce_id'

    @api.model
    def _get_finished_workoder_inverse_name(self):
        return 'finished_product_produce_id'

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _update_move_lines(self):
        """ update a move line to save the workorder line data"""
        self.ensure_one()
        if self.lot_id:
            move_lines = self.move_id.move_line_ids.filtered(lambda ml: ml.lot_id == self.lot_id and not ml.lot_produced_ids)
        else:
            move_lines = self.move_id.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_produced_ids)

        # Sanity check: if the product is a serial number and `lot` is already present in the other
        # consumed move lines, raise.
        if self.product_id.tracking != 'none' and not self.lot_id:
            raise UserError(_('Please enter a lot or serial number for %s !' % self.product_id.display_name))

        if self.lot_id and self.product_id.tracking == 'serial' and self.lot_id in self.move_id.move_line_ids.filtered(lambda ml: ml.qty_done).mapped('lot_id'):
            raise UserError(_('You cannot consume the same serial number twice. Please correct the serial numbers encoded.'))

        # Update reservation and quantity done
        for ml in move_lines:
            rounding = ml.product_uom_id.rounding
            if float_compare(self.qty_done, 0, precision_rounding=rounding) <= 0:
                break
            quantity_to_process = min(self.qty_done, ml.product_uom_qty - ml.qty_done)
            self.qty_done -= quantity_to_process

            new_quantity_done = (ml.qty_done + quantity_to_process)
            # if we produce less than the reserved quantity to produce the finished products
            # in different lots,
            # we create different component_move_lines to record which one was used
            # on which lot of finished product
            if float_compare(new_quantity_done, ml.product_uom_qty, precision_rounding=rounding) >= 0:
                ml.write({
                    'qty_done': new_quantity_done,
                    'lot_produced_ids': self._get_produced_lots(),
                })
            else:
                new_qty_reserved = ml.product_uom_qty - new_quantity_done
                default = {
                    'product_uom_qty': new_quantity_done,
                    'qty_done': new_quantity_done,
                    'lot_produced_ids': self._get_produced_lots(),
                }
                ml.copy(default=default)
                ml.with_context(bypass_reservation_update=True).write({
                    'product_uom_qty': new_qty_reserved,
                    'qty_done': 0
                })

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _create_extra_move_lines(self):
        """Create new sml if quantity produced is bigger than the reserved one"""
        vals_list = []
        quants = self.env['stock.quant']._gather(self.product_id, self.move_id.location_id, lot_id=self.lot_id, strict=False)
        # Search for a sub-locations where the product is available.
        # Loop on the quants to get the locations. If there is not enough
        # quantity into stock, we take the move location. Anyway, no
        # reservation is made, so it is still possible to change it afterwards.
        for quant in quants:
            quantity = quant.quantity - quant.reserved_quantity
            quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id, rounding_method='HALF-UP')
            rounding = quant.product_uom_id.rounding
            if (float_compare(quant.quantity, 0, precision_rounding=rounding) <= 0 or
                    float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0):
                continue
            vals = {
                'move_id': self.move_id.id,
                'product_id': self.product_id.id,
                'location_id': quant.location_id.id,
                'location_dest_id': self.move_id.location_dest_id.id,
                'product_uom_qty': 0,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': min(quantity, self.qty_done),
                'lot_produced_ids': self._get_produced_lots(),
            }
            if self.lot_id:
                vals.update({'lot_id': self.lot_id.id})

            vals_list.append(vals)
            self.qty_done -= vals['qty_done']
            # If all the qty_done is distributed, we can close the loop
            if float_compare(self.qty_done, 0, precision_rounding=self.product_id.uom_id.rounding) <= 0:
                break

        if float_compare(self.qty_done, 0, precision_rounding=self.product_id.uom_id.rounding) > 0:
            vals = {
                'move_id': self.move_id.id,
                'product_id': self.product_id.id,
                'location_id': self.move_id.location_id.id,
                'location_dest_id': self.move_id.location_dest_id.id,
                'product_uom_qty': 0,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': self.qty_done,
                'lot_produced_ids': self._get_produced_lots(),
            }
            if self.lot_id:
                vals.update({'lot_id': self.lot_id.id})

            vals_list.append(vals)

        return vals_list

    # method in v13 'mrp_abstract_workorder' but not in v12
    def _get_produced_lots(self):
        return self.move_id in self._get_production().move_raw_ids and self._get_final_lots() and [(4, lot.id) for lot in self._get_final_lots()]

    # method in v13 'mrp_product_produce' but not in v12
    def _get_production(self):
        product_produce_id = self.raw_product_produce_id or self.finished_product_produce_id
        return product_produce_id.production_id

    # method in v13 'mrp_product_produce' but not in v12
    def _get_final_lots(self):
        product_produce_id = self.raw_product_produce_id or self.finished_product_produce_id
        return product_produce_id.finished_lot_id | product_produce_id.finished_workorder_line_ids.mapped('lot_id')
