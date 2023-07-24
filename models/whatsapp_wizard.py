# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api, exceptions, _
from passlib.context import CryptContext
import random
import string
from odoo.exceptions import UserError, Warning
import requests


class WhatsappWizard(models.TransientModel):
    _name = 'whatsapp.wizard'

    template_id = fields.Many2one('mail.template', 'Email Template')
    partner = fields.Many2one('res.partner', 'Partner')
    application = fields.Many2one('partner.application')

    def preview_message(self):
        # Perform preview logic
        # This method will be called when the user clicks the "Preview" button
        # You can implement your own logic to preview the email based on the selected template
        print(self.read())
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'context': "{'default_template_id' : %d, 'default_use_template': True, 'default_res_id': %d}" % (self.template_id.id, self.application.id),
            'view_mode': 'form',
            'target': 'new',
        }

    def send_message(self):
        # Perform send logic
        # This method will be called when the user clicks the "Send" button
        # You can implement your own logic to send the email based on the selected template
        print(self.read())
        print('wow')

        url = 'https://graph.facebook.com/v17.0/100112769763111/messages'
        headers = {
            'Authorization': 'Bearer EAAIMh5RFSGsBAJtCqNp5cM4Hanm2W6pHuoz0tEI5ZBp7zA3k0cZBugiB79j6h4GBmeUdeddyakybxNOcoZAZCTwSH3lIcr1EpWZBOGZAA8WhSDOVeyfYsTaAGW7ZC384sHSfgEUCWVGso2ZBcaIhoSZC6O9ZAd5TMJVMLjBC1farZCoVdSd3ZBwL8JtvIsi8tZCD3G2mBcvAWJGuckAZDZD',
            'Content-Type': 'application/json'
        }

        data = {
            'messaging_product': 'whatsapp',
            'to': '19718000092',
            'type': 'template',
            'template': {
                'name': 'hello_world',
                'language': {'code': 'en_US'}
            }
        }

        response = requests.post(url, headers=headers, json=data)

        print(response.status_code)
        print(response.json())

        return {'type': 'ir.actions.act_window_close'}

