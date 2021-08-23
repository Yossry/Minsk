from odoo import models, api


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.multi
    def name_get(self):
        """Este metodo lo sobreescribimos porque no nos esta pasando en el
        contexto el show_attribute False, supongo que debe tener que ver con un
        error de la nueva api
        """
        context = dict(self._context or {})
        context.update({'show_attribute': False})
        return super(
            ProductAttributeValue, self.with_context(context)
        ).name_get()
