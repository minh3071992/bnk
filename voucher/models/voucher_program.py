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
    voucher_partner_temp_ids = fields.One2many('voucher.partner.temp', 'voucher_program_id', string='Voucher Report')

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

    @api.model
    def create(self, val):
        cus_cat_ids = val['customer_category_ids'][0][2]
        partner = self.env['res.partner'].search([('customer_category_ids', 'in', cus_cat_ids)])
        list1 = {'voucher_program_name': val['name']}
        for x in partner:
            list1['partner_id'] = x.id
            self.env['voucher.partner.temp'].sudo().create(list1)
        return super(VoucherProgram, self).create(val)
    