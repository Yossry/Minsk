import time
import pdb
from odoo import tools
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import models, fields, api, _
from lxml import etree
import odoo.addons.decimal_precision as dp

def parse_date(td):
	resYear = float(td.days)/365.0                   # get the number of years including the the numbers after the dot
	resMonth = (resYear - int(resYear))*365.0/30.0  # get the number of months, by multiply the number after the dot by 364 and divide by 30.
	resDays = int((resMonth - int(resMonth))*30)
	resYear = int(resYear)
	resMonth = int(resMonth)
	return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")

def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year, month)[1])
	return datetime(year,month,day)

class hr_documents_expire_type(models.Model):
	_name = 'hr.documents.expire.type'
	_description = 'Expiry Type of Documents'

	name = fields.Char("Document Name")
	remind_days = fields.Integer("Remind Before (Days)")	
	model_id = fields.Many2one('ir.model','Object')	
	document_id = fields.Many2one('ir.model.fields','Attribute')
	code_id = fields.Many2one('ir.model.fields','Code Attribute')
	
class hr_documents_expire(models.Model):
	_name = 'hr.documents.expire'
	_descripion = 'Document Expiry'
	_inherit = ['mail.thread']
	
	@api.model
	def _referencable_models(self):
		lst = []
		lst2 = []		
		models = self.env['hr.documents.expire.type'].search([])
		for x in models:
			if x.model_id.model not in lst2:
				lst2.append(x.model_id.model)
				lst.append((x.model_id.model, x.model_id.name))
		return lst


	@api.one
	@api.depends('date_expiry','remind_days')
	def _calc_days(self):
		start = datetime.strptime(time.strftime(OE_DFORMAT),OE_DFORMAT)
		end = datetime.strptime(self.date_expiry, OE_DFORMAT)
		delta = end - start
		self.days_left = delta.days
		self.expiring = self.remind_days >= self.days_left >= 0


	name = fields.Char("Document Name")
	code = fields.Char("Document Code",track_visibility='onchange')
	doc_type = fields.Char("Object")
	 	
	company_id = fields.Many2one('res.company','Company')
	date_expiry = fields.Date("Date Expired",track_visibility='onchange')
	remind_days = fields.Integer("Remind Before (Days)",track_visibility='onchange')
	days_left = fields.Integer('Days to Expire',compute='_calc_days',store=True)
	expiring = fields.Boolean('Expiring')
	
	refers_to = fields.Reference(selection='_referencable_models',string='Refers To')	 #[('hr.employee','Employee'),('hr.contract','Contract'),('res.company','Cpmpany')]
	document_id = fields.Many2one('hr.documents.expire.type','Document ID')
			
	@api.onchange('document_id','refers_to')
	def onchange_document(self):
		if self.document_id and self.refers_to:			
			self.name = self.document_id.name
			self.date_expiry = eval('self.refers_to.{0}'.format(self.document_id.document_id.name))
			self.company_id = self.refers_to.company_id.id
			self.remind_days = self.document_id.remind_days
			self.doc_type = self.document_id.model_id.name
			if self.document_id.code_id:
				self.code = eval('self.refers_to.{0}'.format(self.document_id.code_id.name))

	@api.model
	def check_new_docs(self):		
		for doc_type in self.env['hr.documents.expire.type'].search([]):
			recs = self.search([('document_id','=',doc_type.id)]) and self.search([('document_id','=',doc_type.id)]).mapped('refers_to').ids or []
			for new_rec in self.env[doc_type.model_id.model].search([('id','not in',recs)]):
				new_rec._get_latest_passport()
				if eval('new_rec.{0}'.format(doc_type.document_id.name)):
					values = {
						'name' : doc_type.name,
						'date_expiry' : eval('new_rec.{0}'.format(doc_type.document_id.name)),
						'company_id' : new_rec.company_id and new_rec.company_id.id or False,
						'remind_days' : doc_type.remind_days,						
						'refers_to' : '{0},{1}'.format(doc_type.model_id.model,new_rec.id),
						'document_id' : doc_type.id,
						'doc_type' : doc_type.model_id.name 							
					}
					if doc_type.code_id:
						values.update({'code' : eval('new_rec.{0}'.format(doc_type.code_id.name))})
					self.create(values)	
	
	@api.model
	def check_modified_docs(self):		
		for doc in self.env['hr.documents.expire'].search([]):			
			doc._calc_days()
			if eval('doc.refers_to.{0}'.format(doc.document_id.document_id.name)) != doc.date_expiry:				
				doc.date_expiry = eval('doc.refers_to.{0}'.format(doc.document_id.document_id.name))
			
			if eval('doc.refers_to.{0}'.format(doc.document_id.code_id.name)) != doc.code:
				doc.code = eval('doc.refers_to.{0}'.format(doc.document_id.code_id.name))

class hr_job(models.Model):
	_inherit = 'hr.job'
	
	@api.multi
	def _no_of_contracts(self):
		res = {}
		for job in self:
			contract_ids = self.env['hr.contract'].search([('job_id', '=', job.id),('state', '!=', 'done')])
		nb = len(contract_ids or [])
		res[job.id] = {'no_of_employee': nb,'expected_employees': nb + job.no_of_recruitment,}
		return res

	def _get_job_position(self):
		res = []
		for contract in self.env['hr.contract'].browse(self):
			if contract.job_id:
				res.append(contract.job_id.id)
		return res
		
	category_ids = fields.Many2many('hr.employee.category','job_category_rel','job_id','category_id',string='Associated Tags')
	no_of_employee = fields.Integer('Current Number of Employees',compute='_no_of_contracts',help='Number of employees currently occupying this job position.')
	expected_employees = fields.Integer('Total Forecasted Employees',compute='_no_of_contracts',help='Expected number of employees for this job position after new recruitment.')

class hr_department(models.Model):
	_inherit = "hr.department"

	@api.one
	@api.depends('code','name')
	def _get_dept_name(self):
		self.short_name = (self.code or '') + ":" + self.name
	
	name = fields.Char('Department Name', required=True,translate=True)
	code = fields.Char("Code",size=4)
	abbrev = fields.Char("Abbrev",size=2)
	short_name = fields.Char('Short Name',compute='_get_dept_name',store=True)
	
	user_ids = fields.Many2many('res.users','department_user_rel','dept_id','user_id','Users')
		
class res_users(models.Model):
	_inherit = 'res.users'

	dept_ids = fields.Many2many('hr.department','department_user_rel','user_id','dept_id','Departments')

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			name = "%s - %s" % (record.login, record.name)
			result.append((record.id, name))
		return result

#class res_company(models.Model):
#	_inherit = 'res.company'
#
#	birthday_mail_template = fields.Many2one('mail.template', 'Birthday Wishes Template', help="This will set the default mail template for birthday wishes.")

class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.model
	def send_birthday_email(self):		
		partner_obj = self.env['res.partner']
		
		wish_template_id = self.env['ir.model.data'].get_object_reference('hr_ext', 'email_template_birthday_wish')[1]
		channel_id = self.env['ir.model.data'].get_object_reference('hr_ext', 'channel_birthday')[1]

		today = datetime.now()
		today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')

		partners = partner_obj.search([('birthday', 'like', today_month_day)])
		for partner in partners:
			if partner.email:
				email_temp = partner.company_id.birthday_mail_template and partner.company_id.birthday_mail_template or self.env['mail.template'].browse(wish_template_id)
				email_temp.send_mail(partner.id, force_send=True)
				
				channel = self.env['mail.channel'].browse(channel_id)
				message = channel.message_post(body=_('Happy Birthday Dear %s.') % (partner.name), partner_ids=[partner.id])
				message.write({'channel_ids':[[6, False, [channel.id]]]})
				partner.message_post(body=_('Happy Birthday.'))
		return None		


