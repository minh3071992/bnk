# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrder(models.Model):
    _inherit = "sale.order"

    voucher_report_ids = fields.Many2many('voucher.report', string='Voucher Report ID')
    has_voucher = fields.Boolean(compute='_compute_has_voucher', string='Has voucher?')
    voucher_ids = fields.One2many('voucher.voucher', 'sale_order_id', string='Voucher used')

    @api.depends('partner_id')
    def _compute_has_voucher(self):
        self.has_voucher = False
        voucher = self.env['voucher.voucher'].sudo().search([('partner_id', '=', self.partner_id.id), ('state', '=', 'ongoing'), ('expiration_date', '>=', datetime.now())])
        if voucher.read(['id']):
            self.has_voucher = True

    def unlink(self):
        vouchers = self.voucher_ids
        for record in vouchers:
            if record.voucher_program_id.state == 'done':
                record.state = 'expired'
            else:
                record.state = 'ongoing'
                record.product_id.lst_price = -record.value
        return super(SaleOrder, self).unlink()

    def write(self, val):
        if len(self.voucher_ids.mapped('id')) != 0:
            product_ids = self.voucher_ids.product_id.mapped('id')
            if val.get('order_line', False):
                for x in val['order_line']:
                    if x[0] == 2:
                        order_line = self.env['sale.order.line'].sudo().browse([x[1]])
                        if order_line.product_id.id in product_ids:
                            voucher_record = self.env['voucher.voucher'].sudo().search([('product_id.id', '=', order_line.product_id.id)])
                            if voucher_record.voucher_program_id.state == 'done':
                                voucher_record.state = 'expired'
                            else:
                                voucher_record.state = 'ongoing'
                                voucher_record.product_id.lst_price = -voucher_record.value
        return super(SaleOrder, self).write(val)
