# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VoucherProgram(models.Model):
    _name = 'voucher.program'
    _description = 'Voucher Program'

    name = fields.Char(string='Voucher Program', required=True)
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    expiration_date = fields.Datetime(required=True)
    customer_category_ids = fields.Many2many('customer.category', string='Participants')
    voucher_rule_ids = fields.One2many('voucher.rule', 'voucher_program_id', string='Voucher rules')

    @api.constrains('start_date', 'end_date')
    def _check_start_end_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError("End_date must be greater than start_date")
    
    @api.constrains('expiration_date')
    def _check_expiration_date(self):
        for record in self:
            if record.expiration_date < record.create_date:
                raise ValidationError("Expiration date invalid")
    