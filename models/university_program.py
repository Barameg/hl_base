# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api, exceptions, _
from passlib.context import CryptContext
import random
import string
from odoo.exceptions import UserError, Warning
import requests



class UniversityProgram(models.Model):
    _name = 'university.program'
    _description = 'University Program'

    name = fields.Char()
    coordinator = fields.Many2one('res.partner')
    university = fields.Many2one('res.partner')
    documents = fields.One2many('university.program.document', 'program')
    costs = fields.One2many('university.program.cost', 'program')

    @api.model
    def create(self, vals_list):
        recs = super(UniversityProgram, self).create(vals_list)
        products = self.env['product.template']
        for rec in recs:
            list_price = 0.00
            productsToCreate = []
            if rec.costs:
                for cost in rec.costs:
                    list_price += cost.amount
                    productsToCreate.append({
                        'default_code': uuid.uuid4(),
                        'name': f'{cost.name} {rec.name}',
                        'list_price': cost.amount,
                        'type': 'service',
                        'hl_program': rec.id
                    })
            products.create(productsToCreate)
        return recs
