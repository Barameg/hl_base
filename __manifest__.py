# -*- coding: utf-8 -*-
{
    'name': "hl_base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Barameg",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HL',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'portal',
        'account'
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/partner_application.xml',
        'views/application_service.xml',
        'views/application_service_document.xml',
        'views/country.xml',
        'views/agent.xml',
        'views/student.xml',
        'views/university.xml',
        'views/university_program.xml',
        'views/university_program_document.xml',
        'views/invoice_email_template.xml',
        'portal_views/sidebar.xml',
        'portal_views/mobile_sidebar.xml',
        'portal_views/login.xml',
        'portal_views/signup.xml',
        'portal_views/emailVerification.xml',
        'portal_views/dashboard.xml',
        'portal_views/application.xml',
        'portal_views/notifications.xml',
        'portal_views/success.xml',
        'portal_views/error.xml',
        'actions/partner_application.xml',
        'actions/application_service.xml',
        'actions/application_service_document.xml',
        'actions/country.xml',
        'actions/agent.xml',
        'actions/university.xml',
        'actions/university_program.xml',
        'actions/university_program_document.xml',
        'menus/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
