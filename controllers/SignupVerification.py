# -*- coding: utf-8 -*-
#from odoo.addons.portal.controllers.portal import CustomerPortal, pager as PortalPager
from passlib.context import CryptContext

from odoo import http
from odoo.http import request, Response, redirect_with_hash
from odoo.osv import expression
import json
from xml.sax.saxutils import escape
import base64
from datetime import datetime

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


class SignupVerificationController(http.Controller):
    @http.route('/signupVerification', type='http', auth='public', website=True)
    def signupVerification(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        cookies = http.request.httprequest.cookies
        response = Response()
        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        email = kw.get('email')
        password = kw.get('password')

        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)
        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response.set_cookie('verificationEmail', verificationEmail, path='/')
            data = {
                'logo': agent.image_128.decode() if agent.image_128 else '',
                'agent': partners.browse(agent.id),
            }
            template = request.env['ir.ui.view']._render_template("hl_base.emailVerification", data)
            response.set_data(template)
            return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response.set_cookie('agent_uuid', agent_uuid, path='/')
            response.set_cookie('student_session', student_session, path='/')
            response = redirect_with_hash('/dashboard')
            return response

        for cookie in cookies:
            response.delete_cookie(cookie)
        response = redirect_with_hash('/login')
        return response


    @http.route('/signupVerification/submit', type='http', auth='none', website=True, csrf=False)
    def submit(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        response = Response()
        cookies = http.request.httprequest.cookies
        partners = request.env['res.partner'].sudo()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        verificationCode = kw.get('verificationCode')

        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        if verificationEmail and not verificationCode:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = redirect_with_hash('/signupVerification')
            response.set_cookie('verificationEmail', verificationEmail, path='/')
            return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = redirect_with_hash('/dashboard')
            response.set_cookie('agent_uuid', agent_uuid, path='/')
            response.set_cookie('student_session', student_session, path='/')
            return response

        student = partners.search([
            ('agent', '=', agent.id),
            ('email', '=', verificationEmail)
        ], limit=1)

        if not student:
            response = redirect_with_hash('/signup')
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
            response.set_cookie('verificationEmail', expires=0,  path='/')
            response.set_cookie('student_session', expires=0,  path='/')
            return response
            
        if not student.accountVerified:
            verified = student.verifyAccount(verificationCode)
            if not verified:
                response = redirect_with_hash('/verificationError')
                response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
                response.set_cookie('verificationEmail', student.email,  path='/')
                response.set_cookie('student_session', expires=0,  path='/')
                return response

            response = redirect_with_hash('/verificationSuccess')
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
            response.set_cookie('verificationEmail', expires=0,  path='/')
            response.set_cookie('student_session', expires=0,  path='/')
            return response

        response = redirect_with_hash('/dashboard')
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        response.set_cookie('student_session', student.student_session, path='/')
        return response

    @http.route('/verificationError', type='http', auth='none', website=True, csrf=False)
    def verificationError(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        response = Response()
        cookies = http.request.httprequest.cookies
        partners = request.env['res.partner'].sudo()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        # if verificationEmail:
        #     for cookie in cookies:
        #         response.delete_cookie(cookie)
        #     response = redirect_with_hash('/signupVerification')
        #     response.set_cookie('verificationEmail', verificationEmail, path='/')
        #     return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = redirect_with_hash('/dashboard')
            response.set_cookie('agent_uuid', agent_uuid, path='/')
            response.set_cookie('student_session', student_session, path='/')
            return response
      
        data = {
            'agent': partners.browse(agent.id),
            'message': 'Verification unsuccessful',
            'buttonText': 'Go back',
            'url': '/signupVerification'
        }
        response = Response()
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        template = request.env['ir.ui.view']._render_template("hl_base.error", data)
        response.set_data(template)
        return response

    @http.route('/verificationSuccess', type='http', auth='none', website=True, csrf=False)
    def verificationSuccess(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        response = Response()
        cookies = http.request.httprequest.cookies
        partners = request.env['res.partner'].sudo()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = redirect_with_hash('/signupVerification')
            response.set_cookie('verificationEmail', verificationEmail, path='/')
            return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = redirect_with_hash('/dashboard')
            response.set_cookie('agent_uuid', agent_uuid, path='/')
            response.set_cookie('student_session', student_session, path='/')
            return response
      
        data = {
            'agent': partners.browse(agent.id),
            'message': 'Verification successful',
            'buttonText': 'Login',
            'url': '/login' 
        }
        response = Response()
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        response.set_cookie('verificationEmail', expires=0,  path='/')
        response.set_cookie('student_session', expires=0,  path='/')
        template = request.env['ir.ui.view']._render_template("hl_base.success", data)
        response.set_data(template)
        return response