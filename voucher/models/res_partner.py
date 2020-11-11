# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_category_ids = fields.Many2many('customer.category', string="Customer Category")
    voucher_ids = fields.One2many('voucher.voucher', 'partner_id', string="Vouchers")
