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
    @http.route('/<string:subdomain>', type='http', auth='none', website=True, csrf=False)
    def main(self, subdomain, **kw):
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
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/dashboard' % subdomain)
            response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
            return response

        for cookie in cookies:
            response.delete_cookie(cookie)
        response = request.redirect('/%s/login' % subdomain)
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        return response

    @http.route([
        '/<string:subdomain>/<string:anything>',
        '/<string:subdomain>/dashboard/<string:anything>',
        '/<string:subdomain>/login/<string:anything>',
        '/<string:subdomain>/login/submit/<string:anything>',
        '/<string:subdomain>/signup/<string:anything>',
        '/<string:subdomain>/signup/submit/<string:anything>',
        '/<string:subdomain>/signupVerification/<string:anything>',
        '/<string:subdomain>/signupVerification/submit/<string:anything>',
    ], type='http', auth='none', website=True, csrf=False)
    def redirect(self, subdomain, anything, **kw):
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
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/signupVerification' % subdomain)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            return response

        if agent_uuid and student_session:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response = request.redirect('/%s/dashboard' % subdomain)
            response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
            response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
            return response

        for cookie in cookies:
            response.delete_cookie(cookie)
        # redirect to dashboard page
        response = request.redirect('/%s/login' % subdomain)
        return response

    @http.route('/<string:subdomain>/dashboard', type='http', auth='public', website=True, csrf=False)
    def dashboard(self, subdomain, **kw):
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
            # redirect to agent not found 
            return "Agent not found"

        if verificationEmail:
            for cookie in cookies:
                response.delete_cookie(cookie)
            response.set_cookie('verificationEmail', verificationEmail, path='/%s/' % subdomain)
            response = request.redirect('/%s/signupVerification' % subdomain)
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
                response.set_cookie('agent_uuid', agent_uuid, path='/%s/' % subdomain)
                response.set_cookie('student_session', student_session, path='/%s/' % subdomain)
                template = request.env['ir.ui.view']._render_template("hl_base.dashboard", data)
                response.set_data(template)
                return response

        for cookie in cookies:
            response.delete_cookie(cookie)
        # redirect to dashboard page
        response = request.redirect('/%s/login' % subdomain)
        return response

    @http.route('/<string:subdomain>/logout', type='http', auth='public', website=True, csrf=False)
    def logout(self, subdomain, **kw):
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
            # redirect to agent not found 
            return "Agent not found"

        # redirect to dashboard page
        response = request.redirect('/%s/login' % subdomain)
        response.set_cookie('student_session', expires=0, path='/%s/' % subdomain)
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        return response