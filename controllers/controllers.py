# -*- coding: utf-8 -*-
#from odoo.addons.portal.controllers.portal import CustomerPortal, pager as PortalPager

from odoo import http
from odoo.http import request, Response
from odoo.osv import expression
import json
from xml.sax.saxutils import escape
import base64
from datetime import datetime


def generate_timestamp():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string
    date_string = now.strftime("%y%m%d%H%M%S")
    return date_string


class LoginController(http.Controller):

    @http.route('/login', type='http', auth='public', website=True)
    def login_form(self, **kw):
        return http.request.render('my_module.login_form_template')

    @http.route('/login/submit', type='http', auth='public', website=True)
    def login_submit(self, **kw):
        email = kw.get('email')
        password = kw.get('password')
        if email and password:
            pass


class AgencyPortal(CustomerPortal):
    @http.route('/<string:subdomain>/portal', type='http', auth='none', website=True, csrf=False)
    def agency_portal(self, subdomain, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        student_uuid = cookies.get('student_uuid')
        agents = request.env['res.partner'].sudo()
        students = request.env['res.partner'].sudo()
        if agent_uuid and student_session and student_uuid:
            agents = agents.search_read([
                ('agent_uuid', '=', agent_uuid)
            ], [], limit=1)
            students = students.search([
                ('agent_uuid', '=', agent_uuid),
                ('student_session', '=', student_session),
                ('student_uuid', '=', student_uuid),
            ], [], limit=1)
            for agent in agents:
                for student in students:
                    data = {
                        'logo': base64.b64encode(agent.image_128).decode('utf-8') if agent.image_128 else '',
                        'agent': agent,
                        'student': student,
                    }
                    response = Response()
                    response.set_cookie('agent_uuid', agent.agent_uuid)
                    response.set_cookie('student_session', student.student_session)
                    response.set_cookie('student_uuid', student.student_uuid)
                    template = request.env['ir.ui.view']._render_template("hl_base.dashboard", data)
                    response.set_data(template)
                    return response
            else:
                return 'invalid data'
        else:
            agents = agents.search([
                ('subdomain', '=', subdomain)
            ], limit=1)
            for agent in agents:
                data = {
                    'agent': agents.browse(agent.id),
                }
                response = Response()
                response.set_cookie('agent_uuid', agent.agent_uuid)
                template = request.env['ir.ui.view']._render_template("hl_base.login", data)
                response.set_data(template)
                return response
            else:
                return 'not found'

    @http.route('/<string:subdomain>/login', type='http', auth='none', website=True, csrf=False)
    def agency_portal(self, subdomain, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        student_session = cookies.get('student_session')
        student_uuid = cookies.get('student_uuid')
        agents = request.env['res.partner'].sudo()
        students = request.env['res.partner'].sudo()
        if agent_uuid and student_session and student_uuid:
            agents = agents.search_read([
                ('agent_uuid', '=', agent_uuid)
            ], [], limit=1)
            students = students.search([
                ('agent_uuid', '=', agent_uuid),
                ('student_session', '=', student_session),
                ('student_uuid', '=', student_uuid),
            ], [], limit=1)
            for agent in agents:
                for student in students:
                    data = {
                        'agent': agent,
                        'student': student,
                    }
                    response = Response()
                    response.set_cookie('agent_uuid', agent.agent_uuid)
                    response.set_cookie('student_session', student.student_session)
                    response.set_cookie('student_uuid', student.student_uuid)
                    template = request.env['ir.ui.view']._render_template("hl_base.dashboard", data)
                    response.set_data(template)
                    return response
            else:
                return 'invalid data'
        else:
            agents = agents.search([
                ('subdomain', '=', subdomain)
            ], limit=1)
            for agent in agents:
                data = {
                    'agent': agents.browse(agent.id),
                }
                response = Response()
                response.set_cookie('agent_uuid', agent.agent_uuid)
                template = request.env['ir.ui.view']._render_template("hl_base.login", data)
                response.set_data(template)
                return response
            else:
                return 'not found'


class StudentPortal(CustomerPortal):
    @http.route(['/my', '/my/home'], type='http', auth="none", website=True, csrf=False)
    def home(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        print(session, 'this is session')
        print(http.request.httprequest)
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session)
        ])
        if partner:
            return request.redirect('/')
        else:
            return request.redirect('/')

    @http.route('/', type='http', auth="none", website=True, csrf=False)
    def index(self, **kw):
        print(request.__dict__)
        return request.redirect('/login')

    @http.route('/<str>', type='http', auth="none", website=True, csrf=False)
    def catchall(self, **kw):
        print(request.__dict__)
        return "nothing here"

    @http.route('/login', type='http', auth="none", website=True, csrf=False)
    def login(self, **kw):
        print(request.__dict__)
        print('yaaay')
        return request.render("hl_base.login")

    @http.route('/signup', type='http', auth="none", website=True, csrf=False)
    def signup(self, **kw):
        print(request.__dict__)
        return request.render("hl_base.signup")

    @http.route('/emailVerification', type='http', auth="none", website=True, csrf=False)
    def emailVerification(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        print(session, 'this is session')
        print(http.request.httprequest)
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session)
        ])
        if partner:
            print(partner.verificationCode)
        return request.render("hl_base.emailVerification")

    @http.route('/dashboard', type='http', auth="none", website=True, csrf=False)
    def dashboard(self, **kw):
        return request.render("hl_base.dashboard")

    @http.route('/application', type='http', auth="none", website=True, csrf=False)
    def application(self, **kw):
        return request.render("hl_base.application")


class StudentPortalApi(CustomerPortal):
    @http.route('/api/validateSession', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_validateSession(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        if not partner_id or not session:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session)
        ])
        if partner:
            return {
                'success': True,
                'message': 'Session validated successfully',
                'data': {
                    'accountVerified': partner.accountVerified
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/login', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_login(self, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        if not agent_uuid:
            return {
                'success': False,
                'message': 'Invalid agent',
                'data': {}
            }
        email = request.jsonrequest.get('email')
        password = request.jsonrequest.get('password')
        if not email or not password:
            return {
                'success': False,
                'message': 'Missing Values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        student = partners.search([
            ('email', '=', email),
            ('password', '=', password)
        ])
        if student:
            response = request.make_response(json.dumps({
                'success': True,
                'message': 'Logged in successfully',
                'data': {
                    'session': student.session,
                    'partner': student.id
                }
            }))
            response.set_cookie('student_session', student.student_session)
            return response
        else:
            return {
                'success': False,
                'message': 'Invalid credentials',
                'data': {}
            }

    @http.route('/api/signup', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_signup(self, **kw):
        cookies = http.request.httprequest.cookies
        agent_uuid = cookies.get('agent_uuid')
        if not agent_uuid:
            return {
                'success': False,
                'message': 'Invalid agent',
                'data': {}
            }
        name = request.jsonrequest.get('name')
        email = request.jsonrequest.get('email')
        password = request.jsonrequest.get('password')
        if not name or not email or not password:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        agent = partners.search([
            ('agent_uuid', '=', agent_uuid)
        ])
        student = partners.search([
            ('agent', '=', agent.id),
            ('email', '=', email),
        ])
        if student:
            return {
                'success': False,
                'message': 'Email already exists',
                'data': {}
            }
        student = partners.signup(name, email, password, agent.id)
        if student:
            response = Response(json.dumps({
                'success': True,
                'message': 'Account created successfully',
                'data': {
                    'student': student.id,
                }
            }), content_type='application/json')
            response.set_cookie('student_session', student.student_session)
            return json.loads(response.data)

    @http.route('/api/verifyEmail', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_verifyEmail(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        verificationCode = request.jsonrequest.get('verificationCode')
        if not partner_id or not session or not verificationCode:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            accountVerified = partner.verifyAccount(verificationCode)
            return {
                'success': accountVerified,
                'message': 'Account verified successfully',
                'data': {}
            }
        else:
            return {
                'success': False,
                'message': 'No partner found',
                'data': {}
            }

    @http.route('/api/universities', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_universities(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        if not partner_id or not session:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            universities = partners.search_read([
                ('is_university', '=', True)
            ], ['name'])
            return {
                'success': True,
                'message': 'Request processed successfully',
                'data': {
                    'universities': universities
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/programs', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_programs(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        university = request.jsonrequest.get('university')
        if not partner_id or not session or not university:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            programs = request.env['university.program'].sudo()
            programs = programs.search_read([
                ('university', '=', int(university))
            ], ['name'])
            return {
                'success': True,
                'message': 'Request processed successfully',
                'data': {
                    'programs': programs
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/documents', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_documents(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        program = request.jsonrequest.get('program')
        if not partner_id or not session or not program:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            documents = request.env['university.program.document'].sudo()
            documents = documents.search_read([
                ('program', '=', int(program))
            ], ['name', 'allowed_size', 'allowed_types', 'required'])
            return {
                'success': True,
                'message': 'Request processed successfully',
                'data': {
                    'documents': documents
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/countries', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_countries(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        if not partner_id or not session:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            countries = request.env['res.country'].sudo().search_read([], ['name'])
            return {
                'success': True,
                'message': 'Request processed successfully',
                'data': {
                    'countries': countries
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/states', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_states(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        country = request.jsonrequest.get('country')
        if not partner_id or not session or not country:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        partners = request.env['res.partner'].sudo()
        partner = partners.search([
            ('id', '=', partner_id),
            ('session', '=', session),
        ])
        if partner:
            states = request.env['res.country.state'].sudo()
            states = states.search_read([
                ('country_id', '=', int(country))
            ], ['name'])
            return {
                'success': True,
                'message': 'Request processed successfully',
                'data': {
                    'states': states
                }
            }
        return {
            'success': False,
            'message': 'Unauthorised access',
            'data': {}
        }

    @http.route('/api/applications', method='POST',  type='json', auth="none", website=True, csrf=False)
    def api_applications(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        if not partner_id or not session:
            return {
                'success': False,
                'message': 'Missing values',
                'data': {}
            }
        print(request.jsonrequest)
        application_id = request.jsonrequest.get('id')
        if application_id:
            partners = request.env['res.partner'].sudo()
            partner = partners.search([
                ('id', '=', partner_id),
                ('session', '=', session),
            ])
            if partner:
                applications = request.env['partner.application'].sudo()
                print(application_id)
                domain = [
                    ('partner', '=', partner.id),
                    ('id', '=', int(application_id))
                ]
                fields = [
                    'first_name',
                    'middle_name',
                    'last_name',
                    'gender',
                    'dob',
                    # 'father_first_name',
                    # 'father_last_name',
                    # 'mother_first_name',
                    # 'mother_last_name',
                    'marital_status',
                    'nationality',
                    'passport_number',
                    'passport_issue_date',
                    'passport_expiry_date',
                    #'contact_number',
                    'address_line_1',
                    'address_line_2',
                    'city',
                    'state',
                    #'zipcode',
                    'country',
                    'university',
                    'program'
                ]
                applications = applications.search_read(domain, fields)
                print(applications)
                return {
                    'success': True,
                    'message': 'Request processed successfully',
                    'data': {
                        'applications': applications
                    }
                }
            return {
                'success': False,
                'message': 'Unauthorised access',
                'data': {}
            }
        else:
            partners = request.env['res.partner'].sudo()
            partner = partners.search([
                ('id', '=', partner_id),
                ('session', '=', session),
            ])
            if partner:
                applications = request.env['partner.application'].sudo()
                applications = applications.search_read([
                    ('partner', '=', partner.id)
                ], ['name', 'create_date', 'status'])
                return {
                    'success': True,
                    'message': 'Request processed successfully',
                    'data': {
                        'applications': applications
                    }
                }
            return {
                'success': False,
                'message': 'Unauthorised access',
                'data': {}
            }

    @http.route('/api/saveApplication', method='POST',  type='http', auth="none", website=True, csrf=False)
    def api_saveApplication(self, **kw):
        cookies = http.request.httprequest.cookies
        partner_id = cookies.get('partner')
        session = cookies.get('session')
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'dob',
            #'father_first_name',
            #'father_last_name',
            #'mother_first_name',
            #'mother_last_name',
            'marital_status',
            'nationality',
            'passport_number',
            'passport_issue_date',
            'passport_expiry_date',
#            'contact_number',
            'address_line_1',
            'address_line_2',
            'city',
            # 'state',
#            'zipcode',
            'country',
            'university',
            'program'
        ]
        try:
            json_data = json.loads(escape(request.httprequest.form['jsonData']))
            missing_fields = [field for field in fields if not json_data.get(field)]
            if not partner_id or not session or not all([json_data.get(field) for field in fields]):
                return json.dumps({
                    'success': False,
                    'message': missing_fields,
                    'data': {}
                })
            partners = request.env['res.partner'].sudo()
            partner = partners.search([
                ('id', '=', partner_id),
                ('session', '=', session),
            ])
            if partner:
                programs = request.env['university.program'].sudo()
                program = programs.search([
                    ('university', '=', int(json_data.get('university'))),
                    ('id', '=', int(json_data.get('program'))),
                ])
                if json_data.get('id'):
                    applications = request.env['partner.application'].sudo()
                    application = applications.search([
                        ('partner', '=', partner.id),
                        ('id', '=', int(json_data.get('id')))
                    ])
                    application.write({
                        'first_name': json_data.get('first_name'),
                        'middle_name': json_data.get('middle_name'),
                        'last_name': json_data.get('last_name'),
                        'gender': json_data.get('gender'),
                        'dob': json_data.get('dob'),
                        # 'father_first_name',
                        # 'father_last_name',
                        # 'mother_first_name',
                        # 'mother_last_name',
                        'marital_status': json_data.get('marital_status'),
                        'nationality': False if not json_data.get('nationality') else int(
                            json_data.get('nationality')),
                        'passport_number': json_data.get('passport_number'),
                        'passport_issue_date': json_data.get('passport_issue_date'),
                        'passport_expiry_date': json_data.get('passport_expiry_date'),
                        #            'contact_number',
                        'address_line_1': json_data.get('address_line_1'),
                        'address_line_2': json_data.get('address_line_2'),
                        'city': json_data.get('city'),
                        'state': False if not json_data.get('state') else int(json_data.get('state')),
                        #            'zipcode',
                        'country': False if not json_data.get('country') else int(json_data.get('country')),
                        'university': False if not json_data.get('university') else int(json_data.get('university')),
                        'program': False if not json_data.get('program') else int(json_data.get('program'))
                    })
                    return json.dumps({
                        'success': True,
                        'message': 'Request processed successfully',
                        'data': {}
                    })
                if len(request.httprequest.files) != len(program.documents):
                    return json.dumps({
                        'success': False,
                        'message': [document.name for document in program.documents],
                        'data': {}
                    })
                applications = request.env['partner.application'].sudo()
                application = applications.create({
                    'partner': partner.id,
                    'first_name': json_data.get('first_name'),
                    'middle_name':json_data.get('middle_name'),
                    'last_name':json_data.get('last_name'),
                    'gender': json_data.get('gender'),
                    'dob': json_data.get('dob'),
                    # 'father_first_name',
                    # 'father_last_name',
                    # 'mother_first_name',
                    # 'mother_last_name',
                    'marital_status': json_data.get('marital_status'),
                    'nationality': False if not json_data.get('nationality') else int(
                        json_data.get('nationality')),
                    'passport_number': json_data.get('passport_number'),
                    'passport_issue_date': json_data.get('passport_issue_date'),
                    'passport_expiry_date': json_data.get('passport_expiry_date'),
                    #            'contact_number',
                    'address_line_1': json_data.get('address_line_1'),
                    'address_line_2': json_data.get('address_line_2'),
                    'city': json_data.get('city'),
                    'state': False if not json_data.get('state') else int(json_data.get('state')),
                    #            'zipcode',
                    'country': False if not json_data.get('country') else int(json_data.get('country')),
                    'university': False if not json_data.get('university') else int(json_data.get('university')),
                    'program': False if not json_data.get('program') else int(json_data.get('program'))
                })
                documents = []
                for file in request.httprequest.files.values():
                    if file:
                        print(file.name)
                        # create an ir.attachment record
                        document = [0, False, {
                            'name': file.name,
                            'type': 'binary',
                            'datas': base64.b64encode(file.read()),
                        }]
                        documents.append(document)
                application.name = generate_timestamp()
                application.documents = documents
                return json.dumps({
                    'success': True,
                    'message': 'Request processed successfully',
                    'data': {
                        'application': application.id
                    }
                })
            return json.dumps({
                'success': False,
                'message': 'Unauthorised access',
                'data': {}
            })

        except KeyError:
            # Handle missing key error
            return json.dumps({
                'success': False,
                'message': 'Missing Key Error',
                'data': {}
            })
        except json.JSONDecodeError:
            # Handle JSON parse error
            return json.dumps({
                'success': False,
                'message': 'Server Error',
                'data': {}
            })

