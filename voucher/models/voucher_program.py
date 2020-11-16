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
    voucher_report_ids = fields.One2many('voucher.report', 'voucher_program_id', string='Voucher Report')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done')
    ], required=True, default='draft')
    filter_sale = fields.Float(compute='_get_voucher_report', string='Voucher value')
    voucher_voucher_ids = fields.One2many('voucher.voucher', 'voucher_program_id', string='Voucher')

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
            self.env['voucher.report'].sudo().create(list1)
        return super(VoucherProgram, self).create(val)
    
    def action_report(self):
        form_view_id = self.env.ref('voucher.voucher_program_form_report').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Voucher Program Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.program',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'res_id': self.id,
            'domain': [('voucher_report_ids.voucher_value', '!=', 0)]  
        }
    
    def action_confirm(self):
        self.state = 'confirm'
        list1 = {}
        list2 = {}
        for record in self.voucher_report_ids:
            if record.voucher_value != 0:
                list1['voucher_program_id'] = record.voucher_program_id.id
                list1['partner_id'] = record.partner_id.id
                list1['value'] = record.voucher_value
                self.env['voucher.voucher'].sudo().create(list1)
                list2 = {
                    'name': 'Voucher %s for %s' %(self.name, record.partner_id.name),
                    'type': 'service',
                    'taxes_id': False,
                    'supplier_taxes_id': False,
                    'sale_ok': False,
                    'purchase_ok': False,
                    'invoice_policy': 'order',
                    'lst_price': -record.voucher_value,
                }
                self.env['product.product'].sudo().create(list2)
                voucher = self.env['voucher.voucher'].sudo().search([('voucher_program_id', '=',
                            record.voucher_program_id.id),('partner_id', '=', record.partner_id.id)])
                product = self.env['product.product'].sudo().search([('name', 'like','%%s%')])
        return {}

    def action_done(self):
        self.state = 'done'
        records = self.env['voucher.voucher'].sudo().search([('voucher_program_id', '=', self.id)])
        for record in records:
            record.state = 'expired'
        return {}

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The voucher program name must be unique"),
    ]

    def write(self, val):
        if self.state == 'confirm' or self.state == 'done':
            raise ValidationError('Cannot edite confirm or done voucher program')
        if (val.get['name', False] and val.get['customer_category_ids', False]:
            records = self.voucher_report_ids
            records.unlink()
            cus_cat_ids = val['customer_category_ids'][0][2]
            partner = self.env['res.partner'].search([('customer_category_ids', 'in', cus_cat_ids)])
            list1 = {'voucher_program_name': val['name']}
            for x in partner:
                list1['partner_id'] = x.id
                self.env['voucher.report'].sudo().create(list1)
            return super(VoucherProgram, self).write(val)
        if val.get['name', False]:
            records = self.voucher_report_ids
            list1 = {'voucher_program_name': val['name']}
            records.write(list1)
            return super(VoucherProgram, self).write(val)
        if val.get['customer_category_ids', False]:
            records = self.voucher_reporst_ids
            records.unlink()
            cus_cat_ids = val['customer_category_ids'][0][2]
            partner = self.env['res.partner'].search([('customer_category_ids', 'in', cus_cat_ids)])
            list1 = {'voucher_program_name': self.name}
            for x in partner:
                list1['partner_id'] = x.id
                self.env['voucher.report'].sudo().create(list1)
            return super(VoucherProgram, self).write(val)
        return super(VoucherProgram, self).write(val)
