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


class DashboardController(http.Controller):
    @http.route('/', type='http', auth='none', website=True, csrf=False)
    def main(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]
        
        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

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

        for cookie in cookies:
            response.delete_cookie(cookie)
        response = redirect_with_hash('/login')
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/')
        return response

    @http.route([
        '/<path:anything>',
        '/dashboard/<path:anything>',
        '/login/<path:anything>',
        '/login/submit/<path:anything>',
        '/signup/<path:anything>',
        '/signup/submit/<path:anything>',
        '/signupVerification/<path:anything>',
        '/signupVerification/submit/<path:anything>',
    ], type='http', auth='none', website=True, csrf=False)
    def block_request(self, anything, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        template = request.env['ir.ui.view']._render_template("hl_base.404")
        response.set_data(template)
        return response
        # if verificationEmail:
        #     for cookie in cookies:
        #         response.delete_cookie(cookie)
        #     response = redirect_with_hash('/signupVerification')
        #     response.set_cookie('verificationEmail', verificationEmail, path='/')
        #     return response
        #
        # if agent_uuid and student_session:
        #     for cookie in cookies:
        #         response.delete_cookie(cookie)
        #     response = redirect_with_hash('/dashboard')
        #     response.set_cookie('agent_uuid', agent_uuid, path='/')
        #     response.set_cookie('student_session', student_session, path='/')
        #     return response
        #
        # for cookie in cookies:
        #     response.delete_cookie(cookie)
        # # redirect to dashboard page
        # response = redirect_with_hash('/login')
        # return response

    @http.route('/dashboard', type='http', auth='public', website=True, csrf=False)
    def dashboard(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

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
            response = redirect_with_hash('/signupVerification')
            return response

        if agent_uuid and student_session:
            student = partners.search([
                ('agent', '=', agent.id),
                ('student_session', '=', student_session),
            ])
            if student:
                data = {
                    'logo': agent.image_128.decode() if agent.image_128 else '',
                    'agent': partners.browse(agent.id),
                    'student': partners.browse(student.id),
                }
                for cookie in cookies:
                    response.delete_cookie(cookie)
                response.set_cookie('agent_uuid', agent_uuid, path='/')
                response.set_cookie('student_session', student_session, path='/')
                template = request.env['ir.ui.view']._render_template("hl_base.dashboard", data)
                response.set_data(template)
                return response

        for cookie in cookies:
            response.delete_cookie(cookie)
        # redirect to dashboard page
        response = redirect_with_hash('/login')
        return response

    @http.route('/logout', type='http', auth='public', website=True, csrf=False)
    def logout(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        subdomain = host.split('.')[0]

        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('subdomain', '=', subdomain)
        ], limit=1)

        if not agent:
            template = request.env['ir.ui.view']._render_template("hl_base.404")
            response.set_data(template)
            return response

        response = redirect_with_hash('/login')
        # redirect to dashboard page
        for cookie in cookies:
            response.delete_cookie(cookie)
        return response
