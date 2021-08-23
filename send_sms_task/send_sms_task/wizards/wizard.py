# -*- coding: utf-8 -*-




#---------------------------         Import Libraries ----------------------------

from odoo import models,fields,_,api
from twilio.rest import Client
from odoo.exceptions import UserError

#----------------------------------------------------------------------------------




#-------------------------------------------Class Wizard------------------------------

class Wizard(models.TransientModel):
    _name='send_task.wizard'



    #-----------------------------------------send------------------------------------------
    def send_task(self):
        tasks=self.env['project.task'].browse(self._context.get('active_ids'))
        account_sid = self.env.user.company_id.account_sid
        auth_token =self.env.user.company_id.auth_token
        from_ = self.env.user.company_id.from_

        for task in tasks:
            body = "Hello , your Task is : " +task.name
            self.send_sms(account_sid,auth_token,body,from_,task.user_id.phone)




    def send_sms(self,account_sid,auth_token,body,frm,to):
        if not account_sid:
            raise UserError(_('Set Value For Account Sid'))
        if not auth_token:
            raise UserError(_('Set Value For Auth Token'))
        if not frm:
            raise UserError(_('Set Your Phone'))

        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
            body=body,
            from_=frm,
            to=to)

#--------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

