# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomerCategory(models.Model):
    _name = 'customer.category'
    _description = 'Customer Category'

    name = fields.Char(string='Title', required=True)
    res_partner_ids = fields.Many2many('res.partner', string="Customers")
    voucher_program_ids = fields.Many2many('voucher.program', string="Voucher Programs", readonly=True)
