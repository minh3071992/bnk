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
    using_voucher = fields.Boolean(compute='_compute_using_voucher', string='Using voucher?')

    @api.depends('partner_id')
    def _compute_has_voucher(self):
        self.has_voucher = False
        voucher = self.env['voucher.voucher'].sudo().search([('partner_id', '=', self.partner_id.id), ('state', '=', 'ongoing'), ('expiration_date', '>=', datetime.now())])
        if voucher.read(['id']):
            self.has_voucher = True

    @api.depends('voucher_ids')
    def _compute_using_voucher(self):
        self.using_voucher = False
        if len(self.voucher_ids.mapped('id')) > 0:
            self.using_voucher = True

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
        # raise ValidationError(str(val))
        if len(self.voucher_ids.mapped('id')) != 0:
            voucher_applied = self.voucher_ids
            if val.get('partner_id', False):
                raise ValidationError('Plz remove voucher first!!')
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
                            self.voucher_ids = [(5)]
                            return super(SaleOrder, self).write(val)
                        break
                    if x[0] == 1:
                        order_line = self.env['sale.order.line'].sudo().browse([x[1]])
                        if order_line.product_id.id in product_ids:
                            if x[2].get('product_uom_qty', 1) != 1.0:
                                raise ValidationError('Cannot change quantity of voucher')
                    if x[0] == 4:
                        order_line = self.env['sale.order.line'].sudo().browse([x[1]])
                        if order_line.product_id.id in product_ids:
                            if self.amount_untaxed == 0:
                                temp_val = val['order_line'].copy()
                                temp_val.remove(x)
                                val['order_line'] = temp_val
                                # self.write({'order_line': [(2, order_line.id)]})
                                x = (1, order_line.id, {'price_unit': 0})
                                val['order_line'].append(x)
                                self.write(val)
                                product = voucher_applied.product_id
                                product.lst_price = -voucher_applied.value
                                if abs(product.lst_price) > self.amount_untaxed:
                                    product.lst_price = -self.amount_untaxed
                                self.sudo().write({'order_line': [(1, order_line.id, {'price_unit': product.lst_price})]})
                                voucher_applied.sale_order_id = self.id
                                voucher_applied.state = 'used'
                                return {}
            return super(SaleOrder, self).write(val)
        else:
            return super(SaleOrder, self).write(val)

    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        if len(self.voucher_ids.mapped('id')) != 0:
            voucher_applied = self.voucher_ids
            product = voucher_applied.product_id
            order_line = self.order_line.search([('product_id', '=', product.id)])
            self.sudo().write({'order_line': [(2, order_line.id)]})
            self.voucher_ids = [(3, self.voucher_ids.mapped('id'))]
