
from odoo import api, models
from odoo.modules import get_resource_path


class PartnerPDF(models.AbstractModel):
	_name = 'report.aarsol_common.partner_fillpdf'
	_inherit = 'report.aarsol_common.abstract'

	@api.model
	def get_original_document_path(self, data, objs):
		return get_resource_path('aarsol_common', 'static/src/pdf', 'partner_pdf.pdf')

	@api.model
	def get_document_values(self, data, objs):
		objs.ensure_one()
		return {'name': objs.name}
