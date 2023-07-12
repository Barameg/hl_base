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
            'name': 'Whatsapp Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner': self.partner.id,
                'default_application': self.id
            },
        }


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
    costs = fields.One2many('university.program.cost', 'program')

    @api.model
    def create(self, vals_list):
        recs = super(UniversityProgram, self).create(vals_list)
        products = self.env['product.template']
        for rec in recs:
            list_price = 0.00
            productsToCreate = []
            if rec.costs:
                for cost in rec.costs:
                    list_price += cost.amount
                    productsToCreate.append({
                        'default_code': uuid.uuid4(),
                        'name': f'{cost.name} {rec.name}',
                        'list_price': cost.amount,
                        'type': 'service',
                        'hl_program': rec.id
                    })
            products.create(productsToCreate)
        return recs


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
    university = fields.Many2one('university', related='program.university')
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

    def import_all_data(self):

        portuguese_pricing_dict = {'IP Leiria - Master Computer engg & mobile computing (2y | Leiria)': {
            '1st payment - Enrollment & Admission': '€1,060.00',
            '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
            '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IPCA -  Master AI (2y | Barcelos)': {'1st payment - Enrollment & Admission': '€585.00',
                                                  '2nd payment -  Pre-Departure & Tuition fees': '€7,745.00',
                                                  '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Leiria - Master International Business (2y)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Portalegre - Master Informatics (2 y | Portalegre)': {
                '1st payment - Enrollment & Admission': '€530.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'IP Portalegre - Technologies for Environmental Recovery and Energy Production (2y)': {
                '1st payment - Enrollment & Admission': '€530.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'IP Portalegre - Master Digital Identity Design (2 y | Portalegre)': {
                '1st payment - Enrollment & Admission': '€530.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'Atlântica - Master Management (2y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€1,040.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€18,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'Atlântica - PG Specialisation Safety Management (1y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€1,040.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'Atlântica - PG Management of Sports Organizations (1y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€1,040.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'IP Leiria - Master Sustainable Tourism Management (2y | Leiria)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'ISAG - Master Business Management (1,5 y | Porto)': {
                '1st payment - Enrollment & Admission': '€1,205.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€12,672.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'Santa Maria - Master in Physiotherapy (1,5 y | Porto)': {
                '1st payment - Enrollment & Admission': '€1,000.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€8,500.00',
                '3rd payment - Post Landing, Customer Care & Development': '€1,900.00'},
            'IP Leiria - Master Civil Engineering – Building Construction (2y | Leiria)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Leiria - Master Electrical and Electronic Engineering (2y | Leiria)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Leiria - Master Graphic Design (2y | Leiria)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Leiria - Master Product Design Engineering (2y | Leiria)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'IP Portalegre - PG Informatics (1 y | Portalegre)': {
                '1st payment - Enrollment & Admission': '€530.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€8,745.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            'University of Porto - Masters Mechanical Engineering (2y | Porto)': {
                '1st payment - Enrollment & Admission': '€555.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'},
            'University of Portucalense - Bachelor Hospitality Management (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€1,252.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€9,445.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            'University of Portucalense -  Masters Tourism and Hospitality (2y | Porto)': {
                '1st payment - Enrollment & Admission': '€1,252.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€15,061.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,360.00'},
            'University of Minho - Masters Structural Analysis of Monuments and Historical Construction (1y | Guimarães)': {
                '1st payment - Enrollment & Admission': '€750.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            'Universidade Europeia - PG Game Design (1y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€1,055.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€7,610.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            "Universidade Catholica Portuguesa - International Bachelor's in Business administration (1st year, 3 yrs total)": {
                '1st payment - Enrollment & Admission': '€1,055.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€11,075.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,460.00'},
            'University of Lisbon - Master Biopharmaceutical Sciences (2y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€575.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€11,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            'University of Lisbon - Master Medicinal and biopharmaceutical chemistry (2y | Lisbon)': {
                '1st payment - Enrollment & Admission': '€575.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€11,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,860.00'},
            'IP Leiria - Bachelor Games and Multimedia (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€1,060.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€7,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,480.00'}}

        lithuanian_pricings_dict = {
            'LSU - Master Tourism and Sports Management (2y)': {'1st payment - Enrollment & Admission': '€680.00',
                                                                '2nd payment -  Pre-Departure & Tuition fees': '€12,527.00',
                                                                '3rd payment - Post Landing, Customer Care & Development': '€4,180.00'},
            'LSU - Master Physiotherapy (2y)': {'1st payment - Enrollment & Admission': '€680.00',
                                                '2nd payment -  Pre-Departure & Tuition fees': '€12,527.00',
                                                '3rd payment - Post Landing, Customer Care & Development': '€3,680.00'},
            'LSU - Bachelor Physiotherapy (1st year, 4 yrs total)': {'1st payment - Enrollment & Admission': '€680.00',
                                                                     '2nd payment -  Pre-Departure & Tuition fees': '€7,769.00',
                                                                     '3rd payment - Post Landing, Customer Care & Development': '€2,840.00'},
            'LSU - Bachelor Tourism and Sports Management (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€680.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€6,949.00',
                '3rd payment - Post Landing, Customer Care & Development': '€2,840.00'}}

        spanish_pricings_dict = {'Squad coding school - Full Stack webdevelopment with PHP Laravel (9m | Barcelona)': {
            '1st payment - Enrollment & Admission': '€550.00',
            '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
            '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Ubiqum - Full stack Web Development with Java (5m | Barcelona)': {
                '1st payment - Enrollment & Admission': '€2,000.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€11,745.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Ubiqum - Data Analytics & Machine Learning (5m | Barcelona)': {
                '1st payment - Enrollment & Admission': '€2,000.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€12,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            "ITTI - Master's program in Cloud Architecture (15m)": {'1st payment - Enrollment & Admission': '€1,500.00',
                                                                    '2nd payment -  Pre-Departure & Tuition fees': '€15,195.00',
                                                                    '3rd payment - Post Landing, Customer Care & Development': '€3,887.50'},
            'ITTI - Master in International Sports Management (8m)': {
                '1st payment - Enrollment & Admission': '€1,500.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'ITTI - Executive program in esports Management (8m)': {'1st payment - Enrollment & Admission': '€1,500.00',
                                                                    '2nd payment -  Pre-Departure & Tuition fees': '€17,245.00',
                                                                    '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'SBS - International Business (12m)': {'1st payment - Enrollment & Admission': '€2,475.00',
                                                   '2nd payment -  Pre-Departure & Tuition fees': '€18,045.00',
                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'SBS -Business Analytics (12m)': {'1st payment - Enrollment & Admission': '€2,475.00',
                                              '2nd payment -  Pre-Departure & Tuition fees': '€18,045.00',
                                              '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Vatel - Bachelor International Hotel Management (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,670.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€14,115.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Business Administration (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Digital Marketing, Transformation & Design Thinking (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Arts in\nCommunication & Public Relations (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Arts in\nDigital Business, Design\n& Innovation (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                   '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Marketing (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                  '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                  '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Finance (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Tourism & Hospitality Management (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Innovation & Entrepreneurship (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Digital Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                         '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                         '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Fashion & Luxury Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                  '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                                  '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in International Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                            '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                            '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Communication & Public Relations (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in International Marketing (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                             '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                             '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Global Banking & Finance (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                              '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                              '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Leisure & Tourism\nManagement (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                   '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Entrepreneurship (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                      '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                      '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Digital Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                      '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                      '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Sports Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                       '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                       '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Human Resources\nManagement (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                 '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                                 '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Blockchain Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                           '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                           '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'}}

        self.handle_dictionary_items(portuguese_pricing_dict)
        self.handle_dictionary_items(spanish_pricings_dict)
        self.handle_dictionary_items(lithuanian_pricings_dict)

    def handle_dictionary_items(self, dictionary):
        for program_name, costs in dictionary.items():
            university = self.search([
                ('name', '=', program_name.split('-')[0].strip())
            ])
            if not university:
                university = self.create({
                    'name': program_name.split('-')[0].strip(),
                    'is_university': True
                })

            program = self.env['university.program'].search([
                ('name', '=', program_name.split('-')[0].strip()),
                ('university', '=', university.id)
            ])

            if not program:
                program = self.env['university.program'].create({
                    'name': program_name.split('-')[1].strip(),
                    'university': university.id
                })

            for cost_name, amount in costs.items():
                cost = self.env['university.program.cost'].search([
                    ('name', '=', cost_name),
                    ('program', '=', program.id)
                ])
                if not cost:
                    cost = self.env['university.program.cost'].create({
                        'name': cost_name,
                        'amount': amount.replace('€', '').replace(',', ''),
                        'program': program.id
                    })

    def import_spanish_fees(self):
        program_pricings_dict = {'Squad coding school - Full Stack webdevelopment with PHP Laravel (9m | Barcelona)': {
            '1st payment - Enrollment & Admission': '€550.00',
            '2nd payment -  Pre-Departure & Tuition fees': '€10,245.00',
            '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Ubiqum - Full stack Web Development with Java (5m | Barcelona)': {
                '1st payment - Enrollment & Admission': '€2,000.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€11,745.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Ubiqum - Data Analytics & Machine Learning (5m | Barcelona)': {
                '1st payment - Enrollment & Admission': '€2,000.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€12,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            "ITTI - Master's program in Cloud Architecture (15m)": {'1st payment - Enrollment & Admission': '€1,500.00',
                                                                    '2nd payment -  Pre-Departure & Tuition fees': '€15,195.00',
                                                                    '3rd payment - Post Landing, Customer Care & Development': '€3,887.50'},
            'ITTI - Master in International Sports Management (8m)': {
                '1st payment - Enrollment & Admission': '€1,500.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€13,245.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'ITTI - Executive program in esports Management (8m)': {'1st payment - Enrollment & Admission': '€1,500.00',
                                                                    '2nd payment -  Pre-Departure & Tuition fees': '€17,245.00',
                                                                    '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'SBS - International Business (12m)': {'1st payment - Enrollment & Admission': '€2,475.00',
                                                   '2nd payment -  Pre-Departure & Tuition fees': '€18,045.00',
                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'SBS -Business Analytics (12m)': {'1st payment - Enrollment & Admission': '€2,475.00',
                                              '2nd payment -  Pre-Departure & Tuition fees': '€18,045.00',
                                              '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'Vatel - Bachelor International Hotel Management (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,670.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€14,115.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Business Administration (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Digital Marketing, Transformation & Design Thinking (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Arts in\nCommunication & Public Relations (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Bachelor of Arts in\nDigital Business, Design\n& Innovation (1st year, 3 yrs total)': {
                '1st payment - Enrollment & Admission': '€2,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€22,495.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                   '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Marketing (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                  '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                  '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Finance (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Tourism & Hospitality Management (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Innovation & Entrepreneurship (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Digital Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                         '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                         '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - Master in Fashion & Luxury Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                  '2nd payment -  Pre-Departure & Tuition fees': '€16,845.00',
                                                                  '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in International Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                            '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                            '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Communication & Public Relations (1 year)': {
                '1st payment - Enrollment & Admission': '€3,700.00',
                '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in International Marketing (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                             '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                             '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Global Banking & Finance (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                              '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                              '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Leisure & Tourism\nManagement (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                   '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                                   '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Entrepreneurship (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                      '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                      '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Digital Business (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                      '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                      '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Sports Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                       '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                       '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Human Resources\nManagement (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                                 '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                                 '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'},
            'EU - MBA in Blockchain Management (1 year)': {'1st payment - Enrollment & Admission': '€3,700.00',
                                                           '2nd payment -  Pre-Departure & Tuition fees': '€23,145.00',
                                                           '3rd payment - Post Landing, Customer Care & Development': '€3,700.00'}}
        # Print the programs and their corresponding pricings
        for program_name, costs in program_pricings_dict.items():
            program = self.env['university.program'].search([
                ('name', '=', program_name.split('-')[1].strip())
            ])
            for cost_name, cost_value in costs.items():
                cost = self.env['university.program.cost'].search([
                    ('name', '=', cost_name),
                    ('program', '=', program.id)
                ])
                if not cost:
                    self.env['university.program.cost'].create({
                        'name': cost_name,
                        'program': program.id,
                        'amount': float(cost_value.replace('€', '').replace(',',''))
                    })

    def import_data(self):
        portugalPrograms = [
            "IP Leiria - Master Computer engg & mobile computing (2y | Leiria)",
            "IPCA -  Master AI (2y | Barcelos)",
            "IP Leiria - Master International Business (2y)",
            "IP Portalegre - Master Informatics (2 y | Portalegre)",
            "IP Portalegre - Technologies for Environmental Recovery and Energy Production (2y)",
            "IP Portalegre - Master Digital Identity Design (2 y | Portalegre)",
            "Atlântica - Master Management (2y | Lisbon)",
            "Atlântica - PG Specialisation Safety Management (1y | Lisbon)",
            "Atlântica - PG Management of Sports Organizations (1y | Lisbon)",
            "IP Leiria - Master Sustainable Tourism Management (2y | Leiria)",
            "ISAG - Master Business Management (1,5 y | Porto)",
            "Santa Maria - Master in Physiotherapy (1,5 y | Porto)",
            "IP Leiria - Master Civil Engineering – Building Construction (2y | Leiria)",
            "IP Leiria - Master Electrical and Electronic Engineering (2y | Leiria)",
            "IP Leiria - Master Graphic Design (2y | Leiria)",
            "IP Leiria - Master Product Design Engineering (2y | Leiria)",
            "IP Portalegre - PG Informatics (1 y | Portalegre)",
            "University of Porto - Masters Mechanical Engineering (2y | Porto)",
            "University of Portucalense - Bachelor Hospitality Management (1st year, 3 yrs total)",
            "University of Portucalense -  Masters Tourism and Hospitality (2y | Porto)",
            "University of Minho - Masters Structural Analysis of Monuments and Historical Construction (1y | Guimarães)",
            "Universidade Europeia - PG Game Design (1y | Lisbon)",
            "Universidade Catholica Portuguesa - International Bachelor's in Business administration (1st year, 3 yrs total)",
            "University of Lisbon - Master Biopharmaceutical Sciences (2y | Lisbon)",
            "University of Lisbon - Master Medicinal and biopharmaceutical chemistry (2y | Lisbon)",
            "IP Leiria - Bachelor Games and Multimedia (1st year, 3 yrs total)"
        ]

        spainPrograms = [
            "Squad coding school - Full Stack webdevelopment with PHP Laravel (9m | Barcelona)",
            "Ubiqum - Full stack Web Development with Java (5m | Barcelona)",
            "Ubiqum - Data Analytics & Machine Learning (5m | Barcelona)",
            "ITTI - Master's program in Cloud Architecture (15m)",
            "ITTI - Master in International Sports Management (8m)",
            "ITTI - Executive program in esports Management (8m)",
            "SBS - International Business (12m)",
            "SBS -Business Analytics (12m)",
            "Vatel - Bachelor International Hotel Management (1st year, 3 yrs total)",
            "EU - Bachelor of Business Administration (1st year, 3 yrs total)",
            "EU - Master in Digital Marketing, Transformation & Design Thinking (1 year)",
            "EU - Bachelor of Arts in Communication & Public Relations (1st year, 3 yrs total)",
            "EU - Bachelor of Arts in Digital Business, Design& Innovation (1st year, 3 yrs total)",
            "EU - Master in Management (1 year)",
            "EU - Master in Marketing (1 year)",
            "EU - Master in Finance (1 year)",
            "EU - Master in Tourism & Hospitality Management (1 year)",
            "EU - Master in Innovation & Entrepreneurship (1 year)",
            "EU - Master in Digital Business (1 year)",
            "EU - Master in Fashion & Luxury Business (1 year)",
            "EU - MBA in International Business (1 year)",
            "EU - MBA in Communication & Public Relations (1 year)",
            "EU - MBA in International Marketing (1 year)",
            "EU - MBA in Global Banking & Finance (1 year)",
            "EU - MBA in Leisure & Tourism Management (1 year)",
            "EU - MBA in Entrepreneurship (1 year)",
            "EU - MBA in Digital Business (1 year)",
            "EU - MBA in Sports Management (1 year)",
            "EU - MBA in Human Resources Management (1 year)",
            "EU - MBA in Blockchain Management (1 year)",
        ]

        universities = {}

        for program in portugalPrograms:
            if program.split('-')[0].strip() not in universities:
                universities[program.split('-')[0].strip()] = {
                    'programs': []
                }
            universities[program.split('-')[0].strip()]['programs'].append(program.split('-')[1].strip())

        for program in spainPrograms:
            if program.split('-')[0].strip() not in universities:
                universities[program.split('-')[0].strip()] = {
                    'programs': []
                }
            universities[program.split('-')[0].strip()]['programs'].append(program.split('-')[1].strip())

        for university, programs in universities.items():
            new_university = self.create({
                'name': university,
                'is_university': True
            })
            for program in programs.get('programs'):
                self.env['university.program'].create({
                    'name': program,
                    'university': new_university.id
                })

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

