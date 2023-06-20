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
import random
import string

DEFAULT_CRYPT_CONTEXT = CryptContext(
    ['pbkdf2_sha512', 'plaintext'],
    deprecated=['plaintext'],
)

def clearCookies(response, subdomain):
    cookies = http.request.httprequest.cookies

def generate_timestamp():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string
    date_string = now.strftime("%y%m%d%H%M%S")
    return date_string


class LoginController(http.Controller):
    @http.route('/test', type='http', auth='public', website=True)
    def test(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]
        return 'hello'

    @http.route('/login', type='http', auth='public', website=True)
    def login_form(self, **kw):
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
            'logo': agent.image_128.decode() if agent.image_128 else '',
            'agent': partners.browse(agent.id),
        }
        template = request.env['ir.ui.view']._render_template("hl_base.login", data)
        response.set_data(template)
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        return response

    @http.route('/login/submit', type='http', auth='none', website=True, csrf=False)
    def login_submit(self, **kw):
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

        if email and password:
            student = partners.search([
                ('agent', '=', agent.id),
                ('email', '=', email)
            ], limit=1)
            if not student:
                response = Response()
                response.set_cookie('agent_uuid', agent_uuid, path='/')
                response = redirect_with_hash('/login')
                return response

            valid, replacement = DEFAULT_CRYPT_CONTEXT.verify_and_update(
                password,
                student.password
            )
            if not valid:
                response = Response()
                response = redirect_with_hash('/login')
                response.set_cookie('agent_uuid', agent_uuid, path='/')
                return response

            if not student.accountVerified:
                response = redirect_with_hash('/signupVerification')
                response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
                response.set_cookie('verificationEmail', student.email, path='/')
                return response
            
            response = Response()
            source = string.ascii_letters
            new_session = ''.join(
                (random.choice(source) for _ in range(32))
            )
            student.student_session = new_session
            response = redirect_with_hash('/dashboard')
            response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
            response.set_cookie('student_session', student.student_session, path='/')
            return response

        response = redirect_with_hash('/login')
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        return response

