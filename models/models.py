# -*- coding: utf-8 -*-
import uuid

from odoo import models, fields, api, exceptions, _
from passlib.context import CryptContext
import random
import string
from odoo.exceptions import UserError, Warning

DEFAULT_CRYPT_CONTEXT = CryptContext(
    ['pbkdf2_sha512', 'plaintext'],
    deprecated=['plaintext'],
)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    partner_application = fields.Many2one('partner.application')


class PartnerApplication(models.Model):
    _name = 'partner.application'
    _inherit = ['mail.thread']
    _description = 'partner.application'

    name = fields.Char()
    partner = fields.Many2one('res.partner')
    service = fields.Many2one('application.service')
    documents = fields.One2many('ir.attachment', 'partner_application')
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
        return recs


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


class UniversityProgram(models.Model):
    _name = 'university.program'
    _description = 'University Program'

    name = fields.Char()
    coordinator = fields.Many2one('res.partner')
    university = fields.Many2one('res.partner')
    documents = fields.One2many('university.program.document', 'program')


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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_agent = fields.Boolean(default=False)
    agent_uuid = fields.Char()
    agent_color = fields.Selection([
        ('red', 'RED'),
        ('pink', 'PINK'),
        ('purple', 'PURPLE'),
        ('deep-purple', 'DEEP-PURPLE'),
        ('indigo', 'INDIGO'),
        ('blue', 'BLUE'),
        ('light-blue', 'LIGHT-BLUE'),
        ('cyan', 'CYAN'),
        ('teal', 'TEAL'),
        ('green', 'GREEN'),
        ('light-green', 'LIGHT-GREEN'),
        ('yellow', 'YELLOW'),
        ('amber', 'AMBER'),
        ('orange', 'ORANGE'),
        ('deep-orange', 'DEEP-ORANGE'),
        ('brown', 'BROWN'),
        ('grey', 'GREY'),
        ('blue-grey', 'BLUE-GREY'),
    ], default='indigo')
    agent_secondary_color = fields.Selection([
        ('red', 'RED'),
        ('pink', 'PINK'),
        ('purple', 'PURPLE'),
        ('deep-purple', 'DEEP-PURPLE'),
        ('indigo', 'INDIGO'),
        ('blue', 'BLUE'),
        ('light-blue', 'LIGHT-BLUE'),
        ('cyan', 'CYAN'),
        ('teal', 'TEAL'),
        ('green', 'GREEN'),
        ('light-green', 'LIGHT-GREEN'),
        ('yellow', 'YELLOW'),
        ('amber', 'AMBER'),
        ('orange', 'ORANGE'),
        ('deep-orange', 'DEEP-ORANGE'),
        ('brown', 'BROWN'),
        ('grey', 'GREY'),
        ('blue-grey', 'BLUE-GREY'),
    ], default='indigo')
    agent_shade = fields.Char(default='600')
    agent_secondary_shade = fields.Char(default='400')
    agent = fields.Many2one('res.partner')
    subdomain = fields.Char()
    students = fields.One2many('res.partner', 'agent')
    accountVerified = fields.Boolean(default=False)
    verificationCode = fields.Char()
    password = fields.Char(
        invisible=True,
        copy=False,
    )
    resetPassword = fields.Boolean(
        default=False,
    )
    student_session = fields.Char()
    student_uuid = fields.Char()
    is_student = fields.Boolean(default=False)
    is_university = fields.Boolean(default=False)
    applications = fields.One2many('partner.application', 'partner')
    programs = fields.One2many('university.program', 'university')

    @api.model
    def create(self, values):
        recs = super(ResPartner, self).create(values)
        for rec in recs:
            if not rec.password:
                hashPassword = DEFAULT_CRYPT_CONTEXT.hash if hasattr(
                    DEFAULT_CRYPT_CONTEXT, 'hash'
                ) else DEFAULT_CRYPT_CONTEXT.encrypt
                source = string.ascii_letters
                random_password = ''.join(
                    (random.choice(source) for _ in range(8))
                )
                rec.password = hashPassword(random_password)
            if rec.is_agent:
                rec.agent_uuid = uuid.uuid4()
            if rec.is_student:
                rec.student_uuid = uuid.uuid4()
        return recs

    @api.model
    def signup(self, name=None, email=None, password=None, agent=None):
        if not name or not email or not password or not agent:
            raise exceptions.ValidationError("Missing required value")
        print(name, email, password, agent)
        partner = self.search([
            ('agent', '=', agent),
            ('email', '=', email)
        ])
        if partner:
            raise exceptions.UserError("Email already exists")
        digits = string.digits
        verificationCode = ''.join(
            (random.choice(digits) for _ in range(6))
        )
        print(verificationCode, "============")
        new_partner = self.create({
            'name': name,
            'email': email,
            'password': password,
            'verificationCode': verificationCode,
            'company_type': 'person',
            'agent': agent
        })
        print(new_partner)
        if new_partner:
            mail_values = {
                'email_from': 'support@studyandworkinportugal.com',
                'email_to': new_partner.email,
                'subject': 'Your verification code! | Studay & work in portugal',
                'body_html': f'<p>Dear {new_partner.email},</p><p>Welcome to study and work in portugal! your '
                             f'verification code is {new_partner.verificationCode} </p>',
                'body': f'Dear {new_partner.email}, '
                        f'Welcome to our site! your verification code is {new_partner.verificationCode}',
            }
            mail_id = self.env['mail.mail'].create(mail_values)
            mail_id.send()
            return new_partner
        else:
            raise exceptions.UserError("Server Error")

    @api.model
    def login(self, password=None):
        self.ensure_one()


    @api.model
    def verifyAccount(self, verificationCode=None):
        self.ensure_one()
        if not verificationCode:
            raise exceptions.ValidationError("Missing required value")
        if self.verificationCode == verificationCode:
            self.accountVerified = True
            self.verificationCode = False
        return self.accountVerified

