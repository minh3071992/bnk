# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VoucherPartnerTemp(models.Model):
    _name = 'voucher.partner.temp'
    _description = 'Voucher Report'

    partner_id = fields.Many2one('res.partner', string='Partner ID')
    voucher_program_name = fields.Char(string='Voucher Program Name')
    total_saleorder = fields.Float(compute='_compute_total_saleorder', string='Total sale order')
    voucher_value = fields.Float(compute='_compute_voucher_value', string='Voucher value')
    voucher_program_id = fields.Many2one('voucher.program', compute='_compute_voucher_program_id', string='Voucher Program ID', store=True)
    sale_order_ids = fields.Many2many('sale.order', compute='_compute_sale_order_ids' string='Sale Order')

    def _compute_total_saleorder(self):
        for record in self:
            voucher_program = self.env['voucher.program'].search([('name', '=', record.voucher_program_name)])
            partner = record.partner_id
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', 'in', ('sale', 'done')), ('date_order', '>=', voucher_program.start_date), ('date_order', '<=', voucher_program.end_date)])
            total = sum(sale_orders.mapped('amount_untaxed'))
            record.total_saleorder = total

    def _compute_voucher_value(self):
        for record in self:
            voucher_program = self.env['voucher.program'].search([('name', '=', record.voucher_program_name)])
            voucher_rules = self.env['voucher.rule'].search([('voucher_program_id', '=', voucher_program.id)])
            partner = record.partner_id
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', 'in', ('sale', 'done')), ('date_order', '>=', voucher_program.start_date), ('date_order', '<=', voucher_program.end_date)])
            total = sum(sale_orders.mapped('amount_untaxed'))
            voucher_rate = 0
            for x in voucher_rules:
                if x.min_quantity == 0:
                    if total < x.max_quantity:
                        voucher_rate = x.rate
                        break
                if x.max_quantity == 0:
                    if total > x.min_quantity:
                        voucher_rate = x.rate
                        break
                if x.min_quantity < total <= x.max_quantity:
                    voucher_rate = x.rate
                    break
            vouchervalue = total * (voucher_rate / 100)
            record.voucher_value = vouchervalue

    @api.depends('voucher_program_name')    
    def _compute_voucher_program_id(self):
        for record in self:
            record.voucher_program_id = self.env['voucher.program'].search([('name', '=', record.voucher_program_name)])
    
    def _compute_sale_order_ids(self):
        for record in self:
            voucher_program = self.env['voucher.program'].search([('name', '=', record.voucher_program_name)])
            partner = record.partner_id
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', 'in', ('sale', 'done')), ('date_order', '>=', voucher_program.start_date), ('date_order', '<=', voucher_program.end_date)])
            record.sale_order_ids = (6, 0 , sale_orders.mapped('id'))
