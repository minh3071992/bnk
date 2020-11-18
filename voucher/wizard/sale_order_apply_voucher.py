from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleVoucherApplyCode(models.TransientModel):
    _name = 'sale.voucher.apply.code'
    _rec_name = 'voucher_code'
    _description = 'Sales Voucher Apply Code'

    voucher_code = fields.Char(string="Code", required=True)

    def apply_voucher(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        voucher = self.env['voucher.voucher'].search([('partner_id', '=', sale_order.partner_id.id), ('state', '=', 'ongoing'), ('expiration_date', '>=', datetime.now())])
        voucher_applied = voucher.search([('name', '=', self.voucher_code)])
        if not voucher_applied:
            raise ValidationError('Wrong voucher code')
        product = voucher_applied.product_id
        if abs(product.lst_price) > sale_order.amount_untaxed:
            product.lst_price = -sale_order.amount_untaxed
        sale_order.sudo().write({'order_line': [(0, False, {'name': product.name, 'product_id': product.id, 'price_unit': product.lst_price, 'product_uom_qty': 1.0, 'product_uom': 1, 'tax_id': []})]})
        voucher_applied.sale_order_id = sale_order.id
        voucher_applied.state = 'used'
        return {}