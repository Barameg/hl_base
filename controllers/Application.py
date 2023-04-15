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


    @http.route('/<string:subdomain>/application/submit', type='http', auth='none', website=True, csrf=False)
    def application_submit(self, subdomain, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        email = cookies.get('email')
        print(kw)