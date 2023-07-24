# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api, exceptions, _
from passlib.context import CryptContext
import random
import string
from odoo.exceptions import UserError, Warning
import requests

DEFAULT_CRYPT_CONTEXT = CryptContext(
    ['pbkdf2_sha512', 'plaintext'],
    deprecated=['plaintext'],
)


# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'
#
#     partner_application = fields.Many2one('partner.application')


class ApplicationService(models.Model):
    _name = 'application.service'
    _description = 'application.service'

    name = fields.Char()
    documents = fields.One2many('application.service.document', 'service')


class ApplicationServiceDocument(models.Model):
    _name = 'application.service.document'
    _description = 'application.service.document'

    name = fields.Char()
    service = fields.Many2one('application.service')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hl_program = fields.Many2one('university.program')


class AccountMove(models.Model):
    _inherit = 'account.move'

    programs = fields.Many2many('university.program')

    def email_invoice(self):
        template = self.env.ref('hl_base.invoice_email_template')  # Replace 'module_name' with the actual module name containing the template

        email_values = {
            'email_from': self.env.user.email or '',
            'email_to': self.partner_id.email or '',
            'subject': self.name,
        }
        attachments = self.env['ir.attachment']
        attachment = attachments.search([
            ('res_id', '=', self.id),
            ('res_model', '=', 'account.move'),
        ])
        print(attachment)
        if attachment:
            # Append the attachment to the email values
            email_values['attachment_ids'] = [(4, attachment.id, 0)]
        template.send_mail(self.id, email_values=email_values)

        # mail_values = {
        #     'email_to': self.partner_id.email,
        #     'subject': 'Welcome to our site!',
        #     'body_html': f'<p>Dear {self.partner_id.name},</p><p>Welcome to our site! your verification code is {self.partner_id} </p>',
        #     'body': f'Dear {self.partner_id.name}, Welcome to our site! your verification code is {self.partner_id}',
        # }
        #
        # mail_id = self.env['mail.mail'].create(mail_values)
        # mail_id.send()

    @api.model
    def create(self, vals_list):
        recs = super(AccountMove, self).create(vals_list)
        for rec in recs:
            linesWithPrograms = rec.line_ids.filtered(lambda line: line if line.product_id.hl_program else None)
            programs = linesWithPrograms.mapped(lambda line: line.product_id.hl_program)
            rec.programs = [[6,0,programs.mapped(lambda program: program.id)]]
            rec.email_invoice()
        return recs


class UniversityProgramCost(models.Model):
    _name = 'university.program.cost'
    _description = 'University Program Cost'

    name = fields.Char()
    program = fields.Many2one('university.program')
    university = fields.Many2one(related='program.university')
    amount = fields.Float(default=0.00)


class UniversityProgramDocument(models.Model):
    _name = 'university.program.document'
    _description = 'University Program Document'

    name = fields.Char()
    uuid = fields.Char()
    allowed_size = fields.Integer(string='Size in MB')
    allowed_types = fields.Char()
    file_type = fields.Selection([
        ('doc', 'Document'),
        ('img', 'Image')
    ], default='img')
    required = fields.Boolean(default=True)
    program = fields.Many2one('university.program')
    university = fields.Many2one(related='program.university')
#    template = fields.Binary(attachment=True)
    template = fields.Many2one('ir.attachment')

    @api.model
    def create(self, values):
        recs = super(UniversityProgramDocument, self).create(values)
        for rec in recs:
            if rec.file_type == 'doc':
                doc_types = [
                    'text/plain',
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.ms-powerpoint',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.oasis.opendocument.text',
                    'application/vnd.oasis.opendocument.spreadsheet',
                    'application/vnd.oasis.opendocument.presentation',
                    'application/rtf',
                    #'application/x-latex',
                    #'application/x-tex',
                ]
                mimetypes = ''
                for index, doc_type in enumerate(doc_types):
                    if index < len(doc_types) -1 :
                        mimetypes += doc_type + ', '
                    else:
                        mimetypes += doc_type
                rec.allowed_types = mimetypes
            else:
                img_types = [
                    'image/jpeg',
                    'image/png',
                    'image/gif',
                    'image/webp',
                    'image/svg+xml',
                    'image/bmp',
                    'image/tiff',
                    # 'image/vnd.adobe.photoshop',
                    #'image/x-icon',
                    #'image/jp2',
                    # 'image/vnd.djvu',
                    # 'image/heic',
                    # 'image/heif',
                    # 'image/heic-sequence',
                ]
                mimetypes = ''
                for index, img_type in enumerate(img_types):
                    if index < len(img_types) - 1:
                        mimetypes += img_type + ', '
                    else:
                        mimetypes += img_type
                rec.allowed_types = mimetypes
            rec.uuid = uuid.uuid4()
        return recs

