# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from passlib.context import CryptContext
import random
import string

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
    ])
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
    allowed_size = fields.Integer(string='Size in MB')
    allowed_types = fields.Char()
    required = fields.Boolean(default=True)
    program = fields.Many2one('university.program')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    accountVerified = fields.Boolean(default=False)
    verificationCode = fields.Char()
    password = fields.Char(
        invisible=True,
        copy=False,
    )
    resetPassword = fields.Boolean(
        default=False,
    )
    session = fields.Char()
    is_university = fields.Boolean(default=False)

    programs = fields.One2many('university.program', 'university')

    @api.model
    def create(self, values):
        if not values.get('password'):
            hashPassword = DEFAULT_CRYPT_CONTEXT.hash if hasattr(
                DEFAULT_CRYPT_CONTEXT, 'hash'
            ) else DEFAULT_CRYPT_CONTEXT.encrypt
            source = string.ascii_letters
            random_password = ''.join(
                (random.choice(source) for _ in range(8))
            )
            values['password'] = hashPassword(random_password)
        print(values.get('password'))
        return super(ResPartner, self).create(values)

    @api.model
    def signup(self, name=None, email=None, password=None):
        if not name or not email or not password:
            raise exceptions.ValidationError("Missing required value")
        partner = self.search([
            ('email', '=', email)
        ])
        if partner:
            raise exceptions.UserError("Email already exists")
        source = string.ascii_letters
        session = ''.join(
            (random.choice(source) for _ in range(32))
        )
        verificationCode = ''.join(
            (random.choice(source) for _ in range(32))
        )
        new_partner = self.create({
            'name': name,
            'email': email,
            'password': password,
            'session': session,
            'verificationCode': verificationCode,
            'company_type': 'person'
        })
        if new_partner:
            mail_values = {
                'email_from': 'registration@optimaforma.co',
                'email_to': new_partner.email,
                'subject': 'Welcome to our site!',
                'body_html': f'<p>Dear {new_partner.email},</p><p>Welcome to our site! your verification code is {new_partner.verificationCode} </p>',
                'body': f'Dear {new_partner.email}, Welcome to our site! your verification code is {new_partner.verificationCode}',
            }
            mail_id = self.env['mail.mail'].create(mail_values)
            mail_id.send()
            return new_partner
        else:
            raise exceptions.UserError("Server Error")

    @api.model
    def verifyAccount(self, verificationCode=None):
        self.ensure_one()
        if not verificationCode:
            raise exceptions.ValidationError("Missing required value")
        if self.verificationCode == verificationCode:
            self.accountVerified = True
            self.verificationCode = False
        return self.accountVerified

