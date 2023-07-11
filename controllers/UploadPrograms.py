#from odoo.addons.portal.controllers.portal import CustomerPortal, pager as PortalPager
import csv

from passlib.context import CryptContext

from odoo import http
from odoo.http import request, Response, redirect_with_hash
from odoo.osv import expression
import json
from xml.sax.saxutils import escape
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ApplicationController(http.Controller):
    @http.route('/upload_programs', type='http', auth='none', website=True, csrf=False)
    def upload_programs(self, **kw):
        host = http.request.httprequest.environ.get('HTTP_HOST')
        programs = {}
        universities = {}
        for file in request.httprequest.files.values():
            if file.name == 'programs':
                csv_data = file.read().decode('utf-8')  # Read the file content
                csv_reader = csv.reader(csv_data.splitlines())  # Create a CSV reader
                header = next(csv_reader)  # Read the first row as the header
                # Extract program names from the first column
                program_names = header[1:]

                # Initialize the programs dictionary with empty dictionaries
                for program_name in program_names:
                    if program_name.split('-')[0].strip() not in universities.items():
                        universities[program_name.split('-')[0].strip()] = {}
                        universities[program_name.split('-')[0].strip()]['programs'] = {}
                    universities[program_name.split('-')[0].strip()]['programs'][program_name.split('-')[1].strip()] = {}

                # Iterate over the remaining rows
                for row in csv_reader:
                    pricing_title = row[0]  # Pricing title in the first column
                    pricing_values = row[1:]  # Pricing values in the remaining columns

                    # Populate the program dictionaries with pricing values
                    for program_name, pricing_value in zip(program_names, pricing_values):
                        universities[program_name.split('-')[0].strip()]['programs'][program_name][pricing_title] = pricing_value

        return json.dumps(universities)
