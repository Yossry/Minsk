import time
import pdb
from odoo.osv import expression
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from itertools import groupby
#from odoo.tools import pycompat    by farooq
import base64

import odoo.tools as tools
from odoo import http
from odoo.addons.web.controllers import main as report
import json
import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
#from odoo.tools import html_escape, pycompat      by farooq
from odoo.tools.safe_eval import safe_eval

from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response

def serialize_exception(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			_logger.exception("An exception occured during an http request")
			se = _serialize_exception(e)
			error = {
				'code': 200,
				'message': "Odoo Server Error",
				'data': se
			}
			return werkzeug.exceptions.InternalServerError(json.dumps(error))
	return wrap
    
def grouplines(self, ordered_lines, sortkey):
	grouped_lines = []
	for key, valuesiter in groupby(ordered_lines, sortkey):
		group = {}
		group['category'] = key
		group['lines'] = list(v for v in valuesiter)

		grouped_lines.append(group)
	return grouped_lines


class Company(models.Model):
    _inherit = 'res.company'

    product_printer = fields.Char()
    location_printer = fields.Char()
    shipping_printer = fields.Char()
    product_height = fields.Float(string="Product Height", default=1.0)
    product_width = fields.Float(string="Product Width", default=1.25)
    location_height = fields.Float(string="Location Height", default=1.0)
    location_width = fields.Float(string="Location Width", default=1.25)
    shipping_height = fields.Float(string="Shipping Height", default=1.0)
    shipping_width = fields.Float(string="Shipping Width", default=1.25)
    print_onreceive_product = fields.Boolean(string='Print When Receive Product', help='Print Product Label When Receive Product')
    printer_type = fields.Selection([('zpl', 'ZPL'), ('epl', 'EPL')], string="Type", default="zpl")


class Picking(models.Model):
    _inherit = "stock.picking"

    print_onreceive_product = fields.Boolean(related='company_id.print_onreceive_product', string='Print When Receive Product', help='Print Product Label When Receive Product', store=True)

class ReportController(report.ReportController):
	@http.route([
		'/report/<converter>/<reportname>',
		'/report/<converter>/<reportname>/<docids>',
	], type='http', auth='user', website=True)
	def report_routes(self, reportname, docids=None, converter=None, **data):
		report = request.env['ir.actions.report']._get_report_from_name(reportname)
		context = dict(request.env.context)
				
		if docids:
			docids = [int(i) for i in docids.split(',')]
		if data.get('options'):
			data.update(json.loads(data.pop('options')))
		if data.get('context'):
			# Ignore 'lang' here, because the context in data is the one from the webclient *but* if
			# the user explicitely wants to change the lang, this mechanism overwrites it.
			data['context'] = json.loads(data['context'])
			if data['context'].get('lang'):
				del data['context']['lang']
			context.update(data['context'])

		#if converter == 'html':
		#	html = report.with_context(context).render_qweb_html(docids, data=data)[0]
		#	return request.make_response(html)
		#elif converter == 'pdf':            
		#	pdf = report.with_context(context).render_qweb_pdf(docids, data=data)[0]
		#	pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
		#	return request.make_response(pdf, headers=pdfhttpheaders)
		if converter == 'xls':            
			xls = report.with_context(context).render_qweb_xls(docids, data=data)
			xlshttpheaders = [('Content-Type', 'application/excel'), ('Content-Length', len(xls))]
			return request.make_response(xls, headers=xlshttpheaders)
		if converter == 'ppt':			       
			ppt = report.with_context(context).render_qweb_ppt(docids, data=data)
			ppthttpheaders = [('Content-Type', 'application/powerpoint'), ('Content-Length', len(ppt))]
			return request.make_response(ppt, headers=ppthttpheaders)
		if converter == 'pptp':			       
			pdf = report.with_context(context).render_qweb_ppt(docids, data=data)
			pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
			return request.make_response(pdf, headers=pdfhttpheaders)
		if converter == 'lbl':			       
			pdf = report.with_context(context).render_qweb_lbl(docids, data=data)
			pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
			return request.make_response(pdf, headers=pdfhttpheaders)
		
		return super(ReportController, self).report_routes(reportname, docids, converter, **data)
		#else:
		#	raise werkzeug.exceptions.HTTPException(description='Converter %s not implemented.' % converter)

	@http.route(['/report/download'], type='http', auth="user")
	def report_download(self, data, token):
		"""This function is used by 'qwebactionmanager.js' in order to trigger the download of a pdf/controller report.

		:param data: a javascript array JSON.stringified containg report internal url ([0]) and type [1]
		:returns: Response with a filetoken cookie and an attachment header 	"""
		
		requestcontent = json.loads(data)
		url, type = requestcontent[0], requestcontent[1]
		try:
			if type == 'qweb-pdf':				
				reportname = url.split('/report/pdf/')[1].split('?')[0]

				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')

				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='pdf')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='pdf', **dict(data))

				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pdf")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
				
			elif type == 'qweb-xls':
				reportname = url.split('/report/pdf/')[1].split('?')[0]

				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')

				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='pdf')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='xls', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "xls")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			
			elif type == 'qweb-ppt':				
				reportname = url.split('/report/pdf/')[1].split('?')[0]				
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')

				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='ppt')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='ppt', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pptx")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pptx")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			
			elif type == 'qweb-pptp':				
				reportname = url.split('/report/pdf/')[1].split('?')[0]				
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')

				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='pptp')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='ppt', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pdf")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
				
			elif type == 'qweb-lbl':				
				reportname = url.split('/report/pdf/')[1].split('?')[0]				
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')

				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='lbl')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='lbl', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pdf")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
				
			else:
				return				
		except Exception as e:
			se = _serialize_exception(e)
			error = {
				'code': 200,
				'message': "Odoo Server Error",
				'data': se
			}
			return request.make_response(html_escape(json.dumps(error)))

class ReportAction(models.Model):
	_inherit = 'ir.actions.report'
    
	report_type = fields.Selection(selection_add=[
		('qweb-xls', "XLS"),
		('qweb-ppt', 'PPT'),
		('qweb-pptp', 'PPT-PDF'),
		('qweb-lbl', 'Label'),
	])
    
	#report_type = fields.Selection([
	#	('qweb-html', 'HTML'), 
	#	('qweb-pdf', 'PDF'),
	#	('qweb-xls', 'XLS'),
	#	('qweb-ppt', 'PPT'),
	#	('qweb-pptp', 'PPT-PDF'),
	#	('qweb-lbl', 'Label'),
	#], required=True, default='qweb-html',
	#	help='The type of the report that will be rendered, each one having its own rendering method.'
	#		'HTML means the report will be opened directly in your browser'
	#		'PDF means the report will be rendered using Wkhtmltopdf and downloaded by the user.')
	
	@api.model
	def _get_report_from_name(self, report_name):
		res = super(ReportAction, self)._get_report_from_name(report_name)		
		if res:
			return res
		report_obj = self.env['ir.actions.report']
		qwebtypes = ['qweb-xls','qweb-ppt','qweb-pptp','qweb-lbl']
		conditions = [('report_type', 'in', qwebtypes), ('report_name', '=', report_name)]
		context = self.env['res.users'].context_get()
		return report_obj.with_context(context).search(conditions, limit=1)

		
		#"""Get the first record of ir.actions.report having the ``report_name`` as value for the field report_name."""
		#report_obj = self.env['ir.actions.report']
		#qwebtypes = ['qweb-pdf', 'qweb-html','qweb-xls','qweb-ppt','qweb-pptp','qweb-lbl']
		#conditions = [('report_type', 'in', qwebtypes), ('report_name', '=', report_name)]
		#context = self.env['res.users'].context_get()
		#return report_obj.with_context(context).search(conditions, limit=1)
        
	@api.model
	def render_qweb_xls(self, docids, data=None):
		"""This method generates and returns xls version of a report."""
		# If the report is using a custom model to render its html, we must use it. otherwise, fallback on the generic html rendering.
		report_model_name = 'report.%s' % self.report_name
		report_model = self.env.get(report_model_name)

		if report_model is not None:
			data = report_model.make_excel(data)
		else:
			docs = self.env[self.model].browse(docids)
			data = {
				'doc_ids': docids,
				'doc_model': self.model,
				'docs': docs,
			}
			return self.render_template(self.report_name, data)
		return data

	@api.model
	def render_qweb_ppt(self, docids, data=None):
		"""This method generates and returns ppt version of a report."""
		# If the report is using a custom model to render its html, we must use it. otherwise, fallback on the generic html rendering.
		report_model_name = 'report.%s' % self.report_name
		report_model = self.env.get(report_model_name)

		if report_model is not None:
			data = report_model.make_ppt(data)
		else:
			docs = self.env[self.model].browse(docids)
			data = {
				'doc_ids': docids,
				'doc_model': self.model,
				'docs': docs,
			}
			return docs.ppt5()
		return data

	@api.model
	def render_qweb_lbl(self, docids, data=None):
		"""This method generates and returns ppt version of a report."""
		# If the report is using a custom model to render its html, we must use it. otherwise, fallback on the generic html rendering.
		report_model_name = 'report.%s' % self.report_name
		report_model = self.env.get(report_model_name)

		if report_model is not None:
			data = report_model.make_ppt(data)
		else:
			docs = self.env[self.model].browse(docids)
			data = {
				'doc_ids': docids,
				'doc_model': self.model,
				'docs': docs,
			}
			return docs.label_pdf()
		return data
		
class MailTemplate(models.Model):
	_inherit = "mail.template"
	
	@api.multi
	def generate_email(self, res_ids, fields=None):
		"""Generates an email from the template for given the given model based on
			records given by res_ids.

		:param template_id: id of the template to render.
		:param res_id: id of the record to use for rendering the template (model 
			is taken from template definition)
		:returns: a dict containing all relevant fields for creating a new
			mail.mail entry, with one extra key ``attachments``, in the
				format [(report_name, data)] where data is base64 encoded.
		"""
		self.ensure_one()
		multi_mode = True
		if isinstance(res_ids, pycompat.integer_types):
			res_ids = [res_ids]
			multi_mode = False
		if fields is None:
			fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date']

		res_ids_to_templates = self.get_email_template(res_ids)

		# templates: res_id -> template; template -> res_ids
		templates_to_res_ids = {}
		for res_id, template in res_ids_to_templates.items():
			templates_to_res_ids.setdefault(template, []).append(res_id)

		results = dict()
		for template, template_res_ids in templates_to_res_ids.items():
			Template = self.env['mail.template']
			# generate fields value for all res_ids linked to the current template
			if template.lang:
				Template = Template.with_context(lang=template._context.get('lang'))
			for field in fields:
				Template = Template.with_context(safe=field in {'subject'})
				generated_field_values = Template.render_template(
					getattr(template, field), template.model, template_res_ids,
					post_process=(field == 'body_html'))
				for res_id, field_value in generated_field_values.items():
					results.setdefault(res_id, dict())[field] = field_value
			# compute recipients
			if any(field in fields for field in ['email_to', 'partner_to', 'email_cc']):
				results = template.generate_recipients(results, template_res_ids)
			# update values for all res_ids
			for res_id in template_res_ids:
				values = results[res_id]
				# body: add user signature, sanitize
				if 'body_html' in fields and template.user_signature:
					signature = self.env.user.signature
					if signature:
						values['body_html'] = tools.append_content_to_html(values['body_html'], signature, plaintext=False)
				if values.get('body_html'):
					values['body'] = tools.html_sanitize(values['body_html'])
				# technical settings
				values.update(
					mail_server_id=template.mail_server_id.id or False,
					auto_delete=template.auto_delete,
					model=template.model,
					res_id=res_id or False,
					attachment_ids=[attach.id for attach in template.attachment_ids],
				)

            # Add report in attachments: generate once for all template_res_ids
			if template.report_template:
				for res_id in template_res_ids:
					attachments = []
					report_name = self.render_template(template.report_name, template.model, res_id)
					report = template.report_template
					report_service = report.report_name

					if report.report_type not in ['qweb-html', 'qweb-pdf','qweb-pptp']:
						raise UserError(_('Unsupported report type %s found.') % report.report_type)
					result, format = report.render_qweb_pdf([res_id])

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + format
					if not report_name.endswith(ext):
						report_name += ext
					attachments.append((report_name, result))
					results[res_id]['attachments'] = attachments
		return multi_mode and results or results[res_ids[0]]
		

# class AccountBalanceReport(models.TransientModel):
# 	_inherit = "aarsol_common.balance.report"
    
# 	level = fields.Integer('Display Level',default=1)
    
# 	@api.multi
# 	def check_report(self):
# 		res = super(AccountBalanceReport, self).check_report()
# 		if res.get('data', False):
# 			if res['data'].get('form', False):
# 				res['data']['form'].update(self.read(['level'])[0])
# 		return res
        
        
    
class res_partner(models.Model):
	_inherit = 'res.partner'

	code = fields.Char('Code')

	@api.multi
	@api.depends('name','code')	
	def name_get(self):
		result = []
		for partner in self:
			name = partner.name
			if partner.code:
				name = partner.code + '-' + name
			result.append((partner.id, name))
		return result 

	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []		
		if name:
			domain = ['|',('code', '=ilike', '%' + name + '%'),('name', operator, name)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		recs = self.search(domain + args, limit=limit)
		return recs.name_get()

class AccountSection(models.Model):
	_name = "account.section"
	_description = "Account Sections"

	code = fields.Char('Section Code',translate=True)
	name = fields.Char('Section Name',required=True,translate=True)
	parent_id = fields.Many2one('account.section','Parent Section')

	@api.multi
	@api.depends('code', 'name')
	def name_get(self):
		result = []
		for line in self:
			result.append((line.id, (line.code or '') + ' - ' + (line.name or '')))			
		return result
		
	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []		
		if name:
			domain = ['|',('code', '=ilike', '%' + name + '%'),('name', operator, name)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		recs = self.search(domain + args, limit=limit)
		return recs.name_get()	

class AccountAccount(models.Model):
	_inherit = 'account.account'
	_rec_name = 'code'

	account_section = fields.Many2one('account.section','Account Section')
	

class AccountJournal(models.Model):
	_inherit = 'account.journal'	

	combine_entry = fields.Boolean('One Combined Entry.')
	
class AccountMove(models.Model):
	_inherit = "account.move"
	_order = 'date desc, name desc, id desc'

	@api.multi
	def write(self, vals):
		res = True
		if 'ref' in vals and not vals['ref']:
			del vals['ref']
		if 'line_ids' in vals:
			res = super(AccountMove, self.with_context(check_move_validity=False)).write(vals)
			self.assert_balanced()
		elif vals:
			res = super(AccountMove, self).write(vals)
		return res

	@api.multi
	def post(self):
		invoice = self._context.get('invoice', False)
		self._post_validate()
		
		for move in self:
			
			move.line_ids.create_analytic_lines()
			if move.name == '/':
				new_name = False
				journal = move.journal_id

				if invoice and invoice.move_name and invoice.move_name != '/':
					new_name = invoice.move_name
				#elif self._context('payment_ref',False):
				#	new_name = self._context('payment_ref')
				else:
					if journal.sequence_id:
						# If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
						sequence = journal.sequence_id
						if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
							sequence = journal.refund_sequence_id

						#new_name = journal.code + '/' + move.date[0:4] + '/' + sequence.with_context(ir_sequence_date=move.date).next_by_id()[8:]
						new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
					else:
						raise UserError(_('Please define a sequence on the journal.'))

				if new_name:
					move.name = new_name
		return self.write({'state': 'posted'})
	

	def move_layout_lines(self,move_id=None):		
		move_lines = self.browse(move_id).line_ids
		sortkey = lambda x: x.section_id if x.section_id else ''
		return grouplines(self, move_lines, sortkey)

	
	@api.multi
	def assert_balanced(self):
		return True
	
	voucher_type = fields.Selection([('general', 'General Voucher'), ('payment', 'Payment Voucher'),('receipt', 'Receipt Voucher'),
		('stock', 'Stock Voucher'), ('asset', 'Asset Voucher')], string='Voucher Type')	
		
	statement_id = fields.Many2one('account.bank.statement')
	voucher_seq = fields.Integer('VSeq')	
			
class AccountMoveLine(models.Model):
	_inherit = "account.move.line"
	_order = 'sequence, date desc, id'
	

	@api.model
	def _get_company(self):		
		context = dict(self._context or {})
		company_id = context.get('company_id', False)
		if company_id:
			return company_id
	
	company_id = fields.Many2one('res.company', related='move_id.company_id', string='Company', store=True,default=_get_company)
	section_id = fields.Many2one('account.move.line.section','Section')	
	sequence = fields.Integer(string='Sequence', default=10)
	
	@api.multi
	@api.depends('move_id')
	def name_get(self):
		result = []
		for line in self:
			if line.debit:
				result.append((line.id, (line.move_id.name if line.move_id.name else '') + ':' + line.name if line.name else '' + '(' + (str(line.debit) if line.debit else '') + ')'))
			else:
				result.append((line.id, (line.move_id.name if line.move_id.name else '') + ':' + line.name if line.name else '' + '(' + (str(line.credit) if line.credit else '') + ')'))
		return result
			
																						

class AccountBankStatementLine(models.Model):
	_inherit = "account.bank.statement.line"
	
	voucher_seq = fields.Integer('V',default=1)
	
		
	def _prepare_reconciliation_move(self, move_ref):
		data = super(AccountBankStatementLine, self)._prepare_reconciliation_move(move_ref)
		data['statement_id'] = self.statement_id.id
		data['voucher_seq'] = self.voucher_seq
				
		return data
	
	def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
		""" Match statement lines with existing payments (eg. checks) and/or payables/receivables (eg. invoices and credit notes) and/or new move lines (eg. write-offs).
			If any new journal item needs to be created (via new_aml_dicts or counterpart_aml_dicts), a new journal entry will be created and will contain those
			items, as well as a journal item for the bank statement line.
			Finally, mark the statement line as reconciled by putting the matched moves ids in the column journal_entry_ids.

			:param self: browse collection of records that are supposed to have no accounting entries already linked.
			:param (list of dicts) counterpart_aml_dicts: move lines to create to reconcile with existing payables/receivables.
				The expected keys are :
				- 'name'
				- 'debit'
				- 'credit'
				- 'move_line'
				    # The move line to reconcile (partially if specified debit/credit is lower than move line's credit/debit)

			:param (list of recordsets) payment_aml_rec: recordset move lines representing existing payments (which are already fully reconciled)

			:param (list of dicts) new_aml_dicts: move lines to create. The expected keys are :
				- 'name'
				- 'debit'
				- 'credit'
				- 'account_id'
				- (optional) 'tax_ids'
				- (optional) Other account.move.line fields like analytic_account_id or analytics_id

			:returns: The journal entries with which the transaction was matched. If there was at least an entry in counterpart_aml_dicts or new_aml_dicts, this list contains
				the move created by the reconciliation, containing entries for the statement.line (1), the counterpart move lines (0..*) and the new move lines (0..*).
		"""
		counterpart_aml_dicts = counterpart_aml_dicts or []
		payment_aml_rec = payment_aml_rec or self.env['account.move.line']
		new_aml_dicts = new_aml_dicts or []

		aml_obj = self.env['account.move.line']

		company_currency = self.journal_id.company_id.currency_id
		statement_currency = self.journal_id.currency_id or company_currency
		st_line_currency = self.currency_id or statement_currency

		counterpart_moves = self.env['account.move']

		# Check and prepare received data
		if any(rec.statement_id for rec in payment_aml_rec):
			raise UserError(_('A selected move line was already reconciled.'))
		for aml_dict in counterpart_aml_dicts:
			if aml_dict['move_line'].reconciled:
				raise UserError(_('A selected move line was already reconciled.'))
			if isinstance(aml_dict['move_line'], pycompat.integer_types):
				aml_dict['move_line'] = aml_obj.browse(aml_dict['move_line'])
		for aml_dict in (counterpart_aml_dicts + new_aml_dicts):
			if aml_dict.get('tax_ids') and isinstance(aml_dict['tax_ids'][0], pycompat.integer_types):
				# Transform the value in the format required for One2many and Many2many fields
				aml_dict['tax_ids'] = [(4, id, None) for id in aml_dict['tax_ids']]
		if any(line.journal_entry_ids for line in self):
			raise UserError(_('A selected statement line was already reconciled with an account move.'))

		# Fully reconciled moves are just linked to the bank statement
		total = self.amount
		for aml_rec in payment_aml_rec:
			total -= aml_rec.debit - aml_rec.credit
			aml_rec.with_context(check_move_validity=False).write({'statement_line_id': self.id})
			counterpart_moves = (counterpart_moves | aml_rec.move_id)

		# Create move line(s). Either matching an existing journal entry (eg. invoice), in which
		# case we reconcile the existing and the new move lines together, or being a write-off.
		if counterpart_aml_dicts or new_aml_dicts:
			st_line_currency = self.currency_id or statement_currency
			st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False

			# Create the move
			self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
			move_vals = self._prepare_reconciliation_move(self.statement_id.name)	
			
			######################  Added search line and make create conditional      #############################
			#move = self.env['account.move'].create(move_vals)
			move = self.env['account.move'].search([('statement_id','=',move_vals['statement_id']),('voucher_seq','=',move_vals['voucher_seq'])])
			if not move:
				move = self.env['account.move'].create(move_vals)
			################   End Change        #############################
			
			counterpart_moves = (counterpart_moves | move)

			# Create The payment
			payment = self.env['account.payment']
			if abs(total)>0.00001:
				partner_id = self.partner_id and self.partner_id.id or False
				partner_type = False
				if partner_id:
					if total < 0:
						partner_type = 'supplier'
					else:
						partner_type = 'customer'

				payment_methods = (total>0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
				currency = self.journal_id.currency_id or self.company_id.currency_id
				payment = self.env['account.payment'].create({
					'payment_method_id': payment_methods and payment_methods[0].id or False,
					'payment_type': total >0 and 'inbound' or 'outbound',
					'partner_id': self.partner_id and self.partner_id.id or False,
					'partner_type': partner_type,
					'journal_id': self.statement_id.journal_id.id,
					'payment_date': self.date,
					'state': 'reconciled',
					'currency_id': currency.id,
					'amount': abs(total),
					'communication': self._get_communication(payment_methods[0] if payment_methods else False),
					'name': self.statement_id.name,
				})

			# Complete dicts to create both counterpart move lines and write-offs
			to_create = (counterpart_aml_dicts + new_aml_dicts)
			ctx = dict(self._context, date=self.date)
			for aml_dict in to_create:
				aml_dict['move_id'] = move.id
				aml_dict['partner_id'] = self.partner_id.id
				aml_dict['statement_line_id'] = self.id
				if st_line_currency.id != company_currency.id:
					aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict['credit']
					aml_dict['currency_id'] = st_line_currency.id
					if self.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
						# Statement is in company currency but the transaction is in foreign currency
						aml_dict['debit'] = company_currency.round(aml_dict['debit'] / st_line_currency_rate)
						aml_dict['credit'] = company_currency.round(aml_dict['credit'] / st_line_currency_rate)
					elif self.currency_id and st_line_currency_rate:
						# Statement is in foreign currency and the transaction is in another one
						aml_dict['debit'] = statement_currency.with_context(ctx).compute(aml_dict['debit'] / st_line_currency_rate, company_currency)
						aml_dict['credit'] = statement_currency.with_context(ctx).compute(aml_dict['credit'] / st_line_currency_rate, company_currency)
					else:
						# Statement is in foreign currency and no extra currency is given for the transaction
						aml_dict['debit'] = st_line_currency.with_context(ctx).compute(aml_dict['debit'], company_currency)
						aml_dict['credit'] = st_line_currency.with_context(ctx).compute(aml_dict['credit'], company_currency)
				elif statement_currency.id != company_currency.id:
					# Statement is in foreign currency but the transaction is in company currency
					prorata_factor = (aml_dict['debit'] - aml_dict['credit']) / self.amount_currency
					aml_dict['amount_currency'] = prorata_factor * self.amount
					aml_dict['currency_id'] = statement_currency.id

			# Create write-offs
			# When we register a payment on an invoice, the write-off line contains the amount
			# currency if all related invoices have the same currency. We apply the same logic in
			# the manual reconciliation.
			counterpart_aml = self.env['account.move.line']
			for aml_dict in counterpart_aml_dicts:
				counterpart_aml |= aml_dict.get('move_line', self.env['account.move.line'])
			new_aml_currency = False
			if counterpart_aml\
					and len(counterpart_aml.mapped('currency_id')) == 1\
					and counterpart_aml[0].currency_id\
					and counterpart_aml[0].currency_id != company_currency:
				new_aml_currency = counterpart_aml[0].currency_id
			for aml_dict in new_aml_dicts:
				aml_dict['payment_id'] = payment and payment.id or False
				if new_aml_currency and not aml_dict.get('currency_id'):
					aml_dict['currency_id'] = new_aml_currency.id
					aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], new_aml_currency)
				aml_obj.with_context(check_move_validity=False, apply_taxes=True).create(aml_dict)

			# Create counterpart move lines and reconcile them
			for aml_dict in counterpart_aml_dicts:
				if aml_dict['move_line'].partner_id.id:
					aml_dict['partner_id'] = aml_dict['move_line'].partner_id.id
				aml_dict['account_id'] = aml_dict['move_line'].account_id.id
				aml_dict['payment_id'] = payment and payment.id or False

				counterpart_move_line = aml_dict.pop('move_line')
				if counterpart_move_line.currency_id and counterpart_move_line.currency_id != company_currency and not aml_dict.get('currency_id'):
					aml_dict['currency_id'] = counterpart_move_line.currency_id.id
					aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], counterpart_move_line.currency_id)
				new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)

				(new_aml | counterpart_move_line).reconcile()

			# Balance the move
			st_line_amount = -sum([x.balance for x in move.line_ids])
			aml_dict = self._prepare_reconciliation_move_line(move, st_line_amount)
			aml_dict['payment_id'] = payment and payment.id or False
			aml_obj.with_context(check_move_validity=False).create(aml_dict)

			#################### Remarked Post Call ############################
			#move.post()
			#record the move name on the statement line to be able to retrieve it in case of unreconciliation
			self.write({'move_name': move.name})
			payment and payment.write({'payment_reference': move.name})
		elif self.move_name:
			raise UserError(_('Operation not allowed. Since your statement line already received a number, you cannot reconcile it entirely with existing journal entries otherwise it would make a gap in the numbering. You should book an entry and make a regular revert of it in case you want to cancel it.'))
		counterpart_moves.assert_balanced()
		return counterpart_moves
				

class account_move_line_section(models.Model):
	_name = "account.move.line.section"
	_description = "Account Move Line Section"

	name = fields.Char('Section')
	code = fields.Char('Code')
	sequence = fields.Integer('Sequence')
	separator = fields.Boolean('Add separator',default=True)


		


