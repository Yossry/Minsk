from base64 import b64encode
from odoo import api, models

BARCODE_FORMAT = """
^XA
^CFA,18
^FO140,10^FD%s^FS

^BY2.5,0.75,100
^FO140,40^BC^FD%s^FS
^XZ
"""


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_print_initial_demand_barcodes(self):
        data = ''
        for picking in self:
            data += ''.join(
                (BARCODE_FORMAT % (l.product_id.name, l.product_id.default_code)) * int(l.product_uom_qty) for l in
                picking.move_lines)

        if data:
            return {
                'shipbox_print': {
                    'endpoint_url': self.env.context.get('endpoint_url', False),
                    'filename': 'initial_demand_barcodes.ZPL',
                    'data': b64encode(data.encode()),
                }
            }
        return True

    @api.multi
    def action_print_operations_barcodes(self):
        data = ''
        for picking in self:
            data += ''.join(
                    (BARCODE_FORMAT % (l.product_id.name, l.product_id.default_code)) * int(l.qty_done) for l in
                    picking.pack_operation_product_ids)

        if data:
            return {
                'shipbox_print': {
                    'endpoint_url': self.env.context.get('endpoint_url', False),
                    'filename': 'operations_barcodes.ZPL',
                    'data': b64encode(data.encode()),
                }
            }
        return True
