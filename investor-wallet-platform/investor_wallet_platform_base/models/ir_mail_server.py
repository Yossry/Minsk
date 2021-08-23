from odoo import fields, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
