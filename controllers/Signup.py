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


class SignupController(http.Controller):

    @http.route('/<string:subdomain>/signup', type='http', auth='public', website=True)
    def signup_form(self, subdomain, **kw):
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

        data = {
            'logo': agent.image_128.decode() if agent.image_128 else '',
            'agent': partners.browse(agent.id),
        }
        template = request.env['ir.ui.view']._render_template("hl_base.signup", data)
        response.set_data(template)
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        return response


    @http.route('/<string:subdomain>/signup/submit', type='http', auth='none', website=True, csrf=False)
    def signup_submit(self, subdomain, **kw):
        cookies = http.request.httprequest.cookies
        response = Response()

        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        verificationEmail = cookies.get('verificationEmail')

        name = kw.get('name')
        email = kw.get('email')
        password = kw.get('password')

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

        student = partners.search([
            ('agent', '=', agent.id),
            ('email', '=', email)
        ], limit=1)

        if student:
            return 'student exist redirect to error page'

        student = partners.signup(name, email, password, agent.id)
        response = request.redirect('/%s/signupVerification' % subdomain)
        response.set_cookie('agent_uuid', agent.agent_uuid, path='/%s/' % subdomain)
        response.set_cookie('verificationEmail', student.email, path='/%s/' % subdomain)
        return response