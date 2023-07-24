# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api, exceptions, _
from passlib.context import CryptContext
import random
import string
from odoo.exceptions import UserError, Warning
import requests


class PartnerApplication(models.Model):
    _name = 'partner.application'
    _inherit = ['mail.thread']
    _description = 'Application'

    name = fields.Char()
    partner = fields.Many2one('res.partner')
    service = fields.Many2one('application.service')
    documents = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', _name)])
    description = fields.Text()
    first_name = fields.Char(string='First Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Surname')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female')
    ], default='m')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    dob = fields.Date(string='Date of Birth')
    father_first_name = fields.Char()
    father_last_name = fields.Char()
    mother_first_name = fields.Char()
    mother_last_name = fields.Char()
    marital_status = fields.Selection([
        ('m', 'Married'),
        ('s', 'Single'),
        ('d', 'Divorced'),
        ('w', 'Widow')
    ])
    nationality = fields.Many2one('res.country')
    passport_number = fields.Char()
    passport_issue_date = fields.Date()
    passport_expiry_date = fields.Date()
    contact_number = fields.Char()
    address_line_1 = fields.Char()
    address_line_2 = fields.Char()
    city = fields.Char()
    state = fields.Many2one('res.country.state')
    zipcode = fields.Char()
    country = fields.Many2one('res.country')
    university = fields.Many2one('res.partner')
    program = fields.Many2one('university.program')
    status = fields.Selection([
        ('new', 'New'),
        ('verification', 'Documents Verification'),
        ('processing', 'Application Processing'),
        ('done', 'Done'),
    ], default='new')

    @api.model
    def create(self, values):
        recs = super(PartnerApplication, self).create(values)
        for rec in recs:
            if not rec.university:
                raise Warning(_("University Cannot be empty"))
            if rec.documents:
                rec.documents.write({
                    'res_model': self._name, 'res_id': rec.id
                })
            rec.name = uuid.uuid4()
            # rec.documents.write({
            #     'res_id': rec.id,
            #     'res_model': self._name
            # })
        return recs

    def open_whatsapp_wizard(self):
        # Open the email wizard popup
        return {
            'name': 'Email Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'email.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner': self.partner.id,
                'default_application': self.id
            },
        }


class EmailWizard(models.TransientModel):
    _name = 'email.wizard'

    template_id = fields.Many2one('mail.template', 'Email Template')
    partner = fields.Many2one('res.partner', 'Partner')
    application = fields.Many2one('partner.application')

    def preview_email(self):
        # Perform preview logic
        # This method will be called when the user clicks the "Preview" button
        # You can implement your own logic to preview the email based on the selected template
        print(self.read())
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'context': "{'default_template_id' : %d, 'default_use_template': True, 'default_res_id': %d}" % (
            self.template_id.id, self.application.id),
            'view_mode': 'form',
            'target': 'new',
        }

    def send_email(self):
        # Perform send logic
        # This method will be called when the user clicks the "Send" button
        # You can implement your own logic to send the email based on the selected template
        if self.template_id.whatsapp_template:
            values = {'header': {}, 'body': {}, 'to': self.application.partner.mobile}
            for variable in self.template_id.whatsapp_template_variables:
                values[variable.type][variable.name] = self.application[variable.template_field.name]
            print(values)
            self.template_id.whatsapp_template.send_template(values)
        return {'type': 'ir.actions.act_window_close'}
