# -*- coding: utf-8 -*-
#from odoo.addons.portal.controllers.portal import CustomerPortal, pager as PortalPager
from passlib.context import CryptContext

from odoo import http
from odoo.http import request, Response
from odoo.osv import expression
import json
from xml.sax.saxutils import escape
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

DEFAULT_CRYPT_CONTEXT = CryptContext(
    ['pbkdf2_sha512', 'plaintext'],
    deprecated=['plaintext'],
)


def generate_timestamp():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string
    date_string = now.strftime("%y%m%d%H%M%S")
    return date_string


class ApplicationController(http.Controller):
    @http.route('/<string:subdomain>/application', type='http', auth='none', website=True, csrf=False)
    def application(self, subdomain, **kw):
        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')
        application_uuid = cookies.get('application_uuid')

        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            return response

        if agent_uuid and student_session:
            if application_uuid:
                applications = request.env['partner.application'].sudo()
                student = partners.search([
                    ('agent', '=', agent.id),
                    ('student_session', '=', student_session),
                ])
                application = applications.search([
                    ('partner', '=', student.id),
                    ('name', '=', application_uuid)
                ], limit=1)
                universities = partners.search([
                    ('is_university', '=', True)
                ])
                programs = request.env['university.program'].sudo().search([])
                documents = request.env['university.program.document'].sudo().search([])
                countries = request.env['res.country'].sudo().search([])
                states = request.env['res.country.state'].sudo().search([])
                data = {
                    'logo': agent.image_128.decode() if agent.image_128 else '',
                    'agent': partners.browse(agent.id),
                    'student': partners.browse(student.id),
                    'universities': universities,
                    'countries': countries,
                    'states': states,
                    'programs': programs,
                    'documents': documents,
                    'application': applications.browse(application.id)
                }   
                response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
    #            response.set_cookie('application_uuid', expires=0, path='/%s/' % subdomain)
                response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
                template = request.env['ir.ui.view']._render_template("hl_base.application", data)
                response.set_data(template)
                return response
            else:
                student = partners.search([
                    ('agent', '=', agent.id),
                    ('student_session', '=', student_session),
                ])
                universities = partners.search([
                    ('is_university', '=', True)
                ])
                programs = request.env['university.program'].sudo().search([])
                documents = request.env['university.program.document'].sudo().search([])
                countries = request.env['res.country'].sudo().search([])
                states = request.env['res.country.state'].sudo().search([])
                data = {
                    'logo': agent.image_128.decode() if agent.image_128 else '',
                    'agent': partners.browse(agent.id),
                    'student': partners.browse(student.id),
                    'universities': universities,
                    'countries': countries,
                    'states': states,
                    'programs': programs,
                    'documents': documents,
                }   
                response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
    #            response.set_cookie('application_uuid', expires=0, path='/%s/' % subdomain)
                response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
                response.set_cookie('email', expires=0, path='/%s/' % subdomain)
                template = request.env['ir.ui.view']._render_template("hl_base.application", data)
                response.set_data(template)
                return response
        for cookie in cookies:
            response.delete_cookie(cookie)
        response = request.redirect('/%s/login' % subdomain)
        # response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
        # response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
        return response
    

        # if not application:
        #     universities = partners.search([
        #         ('is_university', '=', True)
        #     ])
        #     programs = request.env['university.program'].sudo().search([])
        #     countries = request.env['res.country'].sudo().search([])
        #     states = request.env['res.country.state'].sudo().search([])
        #     data = {
        #         'logo': agent.image_128.decode() if agent.image_128 else '',
        #         'agent': partners.browse(agent.id),
        #         'student': partners.browse(student.id),
        #         'universities': universities,
        #         'countries': countries,
        #         'states': states,
        #         'programs': programs
        #     } 
        #     response = Response()
        #     response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        #     response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
        #     response.set_cookie('email', expires=0, path='/%s/' % subdomain)
        #     response.set_cookie('application_uuid', expires=0, path='/%s/' % subdomain)
        #     template = request.env['ir.ui.view']._render_template("hl_base.application", data)
        #     response.set_data(template)
        #     return response
        # universities = partners.search([
        #     ('is_university', '=', True)
        # ])
        # programs = request.env['university.program'].sudo().search([])
        # countries = request.env['res.country'].sudo().search([])
        # states = request.env['res.country.state'].sudo().search([])
        # data = {
        #     'logo': agent.image_128.decode() if agent.image_128 else '',
        #     'agent': partners.browse(agent.id),
        #     'student': partners.browse(student.id),
        #     'application': applications.browse(application.id),
        #     'universities': universities,
        #     'countries': countries,
        #     'states': states,
        #     'programs': programs
        # }
        # print(application.name)
        # response = Response()
        # response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        # response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
        # response.set_cookie('application_uuid', expires=0, path='/%s/' % subdomain)
        # response.set_cookie('email', expires=0, path='/%s/' % subdomain)
        # template = request.env['ir.ui.view']._render_template("hl_base.application", data)
        # response.set_data(template)
        # return response

    @http.route('/<string:subdomain>/application/<string:application_uuid>', type='http', auth='none', website=True, csrf=False)
    def application_edit(self, subdomain, application_uuid, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        email = cookies.get('email')
        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)
        if not agent_uuid:
            if not agent:
                return '404'
            response = request.redirect('/%s/login' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
            response.set_cookie('email', expires=0, path='/%s/' % subdomain)
            return response
        agent_matches_subdomain = partners.search([
            ('subdomain', '=', subdomain),
            ('agent_uuid', '=', agent_uuid),
        ])
        if not agent_matches_subdomain:
            response = request.redirect('/%s/login' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
            response.set_cookie('email', expires=0, path='/%s/' % subdomain)
            return response
        if not student_session:
            if not email:
                response = request.redirect('/%s/login' % subdomain)
                response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
                response.set_cookie('email', expires=0, path='/%s/' % subdomain)
                return response
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
            response.set_cookie('email', email, path='/%s/' % subdomain)
            return response
        student = partners.search([
            ('agent', '=', agent.id),
            ('student_session', '=', student_session),
        ])
        if not student:
            response = request.redirect('/%s/login' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
            response.set_cookie('email', expires=0, path='/%s/' % subdomain)
            return response
        if not student.accountVerified:
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
            response.set_cookie('email', student.email, path='/%s/' % subdomain)
            return response
        applications = request.env['partner.application'].sudo()
        application = applications.search([
            ('partner', '=', student.id),
            ('name', '=', application_uuid)
        ])
        if not application:
            response = request.redirect('/%s/application' % subdomain)
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
            response.set_cookie('email', expires=0, path='/%s/' % subdomain)
            response.set_cookie('application_uuid', expires=0, path='/%s/' % subdomain)
            return response
        universities = partners.search([
            ('is_university', '=', True)
        ])
        programs = request.env['university.program'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        data = {
            'logo': agent.image_128.decode() if agent.image_128 else '',
            'agent': partners.browse(agent.id),
            'student': partners.browse(student.id),
            'application': applications.browse(application.id),
            'universities': universities,
            'countries': countries,
            'states': states,
            'programs': programs
        }
        print(application.name)
        response = Response()
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        response.set_cookie('student_session', student.student_session, path='/%s/' % subdomain)
        response.set_cookie('application_uuid', application.name, path='/%s/' % subdomain)
        response.set_cookie('email', expires=0, path='/%s/' % subdomain)
        template = request.env['ir.ui.view']._render_template("hl_base.application", data)
        response.set_data(template)
        return response

    @http.route('/<string:subdomain>/application/delete/<string:document_template_uuid>', type='http', auth='none', website=True, csrf=False)
    def download_template(self, subdomain, document_template_uuid, **kw):
        pass


    @http.route('/<string:subdomain>/application/delete/<string:application_id>', type='http', auth='none', website=True, csrf=False)
    def application_delete(self, subdomain, application_id, **kw):
        response = Response()
        cookies = http.request.httprequest.cookies

        partners = request.env['res.partner'].sudo()
        applications = request.env['partner.application'].sudo()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            return response
        
        if agent_uuid and student_session:
            student = partners.search([
                ('agent', '=', agent.id),
                ('student_session', '=', student_session),
            ])
            if student:
                application = applications.search([
                    ('name', '=', application_id),
                    ('partner', '=', student.id)
                ])
                if application:
                    application.unlink()
            response = request.redirect('/%s/dashboard' % subdomain)
            response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
            return response
        response = request.redirect('/%s/login' % subdomain)
        response.set_cookie('agent_uuid', expires=0, path='/%s/' % subdomain)
        response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
        return response


    @http.route('/<string:subdomain>/application/submit', type='http', auth='none', website=True, csrf=False)
    def application_submit(self, subdomain, **kw):
        response = Response()
        cookies = http.request.httprequest.cookies

        partners = request.env['res.partner'].sudo()
        countries = request.env['res.country'].sudo()
        states = request.env['res.country.state'].sudo()
        universities = partners.search([
            ('is_university', '=', True)
        ])
        programs = request.env['university.program'].sudo()
        documents = request.env['university.program.document'].sudo()
        applications = request.env['partner.application'].sudo()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            return response

        if agent_uuid and student_session:
            required_fields = [
                'university',
                'program',
                'first_name',
                'middle_name',
                'last_name',
                'gender',
                'dob',
                'marital_status',
                'nationality',
                'passport_number',
                'passport_issue_date',
                'passport_expiry_date',
                'address_line_1',
                'address_line_2',
                'city',
                'country',
            ]

            if any([not kw.get(required_field) for required_field in required_fields]):
                response = request.redirect('/%s/application' % subdomain)
                response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
                return response

            country = countries.search([
                ('id', '=', kw.get('country'))
            ])
            university = universities.search([
                ('id', '=', kw.get('university'))
            ])
            
            program = programs.search([
                ('id', '=', kw.get('program'))
            ])
            
            nationality = countries.search([
                ('id', '=', kw.get('nationality'))
            ])

            if not country or not university or not nationality:
                response = request.redirect('/%s/application' % subdomain)
                response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
                return response

            print(country.state_ids, "========================= state ides")
            print(kw.get('state'), "============================ state selected")

            if country.state_ids and not kw.get('state'):
                response = request.redirect('/%s/application' % subdomain)
                response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
                return response

            state = states.search([
                ('id', '=', kw.get('state'))
            ])
            
            if country.state_ids and not state:
                response = request.redirect('/%s/application' % subdomain)
                response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
                return response

            print(country.state_ids, " ================================ country state ids ")
            student = partners.search([
                ('agent', '=', agent.id),
                ('student_session', '=', student_session),
            ])
            print(student, "=============== here is the student ")
            if not student:
                response = request.redirect('/%s/login' % subdomain)
                response.set_cookie('agent_uuid', expires=0, path='/%s/' % subdomain)
                response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
                return response
            
            print("========================== all good creating application")
            print(kw, "keywords ======================")
            applications.create({
                'university': university.id,
                'partner': student.id,
                'first_name': kw.get('first_name'),
                'middle_name': kw.get('middle_name'),
                'last_name': kw.get('last_name'),
                'gender': kw.get('gender'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'mobile': kw.get('mobile'),
                'dob': kw.get('dob'),
                # father_first_name = fields.Char()
                # father_last_name = fields.Char()
                # mother_first_name = fields.Char()
                # mother_last_name = fields.Char()
                # marital_status = fields.Selection([
                #     ('m', 'Married'),
                #     ('s', 'Single'),
                #     ('d', 'Divorced'),
                #     ('w', 'Widow')
                # ])
                'nationality': kw.get('nationality'),
                'passport_number': kw.get('passport_number'),
                'passport_issue_date': kw.get('passport_issue_date'),
                'passport_expiry_date': kw.get('passport_expiry_date'),
                'contact_number': kw.get('contact_number'),
                'address_line_1': kw.get('address_line_1'),
                'address_line_2': kw.get('address_line_2'),
                'city': kw.get('city'),
                'state': state.id,
                'zipcode': kw.get('zipcode'),
                'country': country.id,
                'university': university.id,
                'program': program.id,
            })
            response = request.redirect('/%s/dashboard' % subdomain)
            response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
            return response

