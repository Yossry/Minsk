
from openerp.osv import fields, osv
import re
from openerp.report.render.rml2pdf import customfonts

class base_config_settings(osv.osv_memory):
	_inherit = 'base.config.settings'
        
	_columns = {
		'birthday_mail_template': fields.many2one('mail.template', 'Birthday Wishes Template', required=True, help='This will set the default mail template for birthday wishes.'),
	}


	def get_default_birthday_mail_template(self, cr, uid, fields, context=None):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		return {'birthday_mail_template': user.company_id.birthday_mail_template.id}

	def set_birthday_mail_template(self, cr, uid, ids, context=None):
		config = self.browse(cr, uid, ids[0], context)
		user = self.pool.get('res.users').browse(cr, uid, uid, context)
		user.company_id.write({'birthday_mail_template': config.birthday_mail_template.id})

