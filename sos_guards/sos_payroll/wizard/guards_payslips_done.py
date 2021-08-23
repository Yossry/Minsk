import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class guards_payslips_done(models.TransientModel):
	_name ='guards.payslips.done'
	_description = 'This Wizard will Change the Payslip into Done State.'
	
	date_from = fields.Date("Start Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])	
	
	def payslip_done(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		
		
		res = self.read(cr, uid, ids, context=context)
		res = res and res[0]
				
		cnt = 0
		
		payslip_obj = self.pool.get('guards.payslip')
		payslip_line_obj = self.pool.get('guards.payslip.line')
		
		slip_ids = payslip_obj.search(cr, uid, [('state','=','draft')], context=context)		
		for slip in payslip_obj.browse(cr, uid, slip_ids, context=context):
			line_ids = payslip_line_obj.search(cr, uid, [('slip_id','=',slip.id),('code','=','BASIC')], context=context)
			
			done = True
			for line in payslip_line_obj.browse(cr, uid, line_ids, context=context):
				post_id = line.post_id.id
				project_id = line.post_id.project_id.id
				
				date_from = res['date_from']
				date_to = res['date_to']
				
				
				if project_id == 30:
					date_from = str(datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
					date_to = str(datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	
							
				cr.execute('''SELECT sum(quantity) qty from guards_payslip gp ,guards_payslip_line gpl \
					where gp.id = gpl.slip_id and gpl.post_id = %s and date_from >= %s and date_to <= %s''',(post_id,date_from,date_to))
				salary = cr.fetchall()
							
				if project_id in (30,32):
					date_from = str(datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
					date_to = str(datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	
							
				cr.execute('''SELECT sum(quantity) qty from account_invoice acinv ,account_invoice_line acinvl \
					where acinv.id = acinvl.invoice_id and acinvl.partner_id = %s and move_id is not NULL and date_invoice between %s and %s''',(post_id,date_from,date_to))
							
				invoice = cr.fetchall()
				
				if salary[0][0] != invoice[0][0]:
					done = False
			
			if done == True:
				
				payslip_obj.guards_process_sheet(cr, uid, [slip.id],context=context)
				cnt  = cnt +1
				if cnt == 80:
					break
				
				
		return True
		



