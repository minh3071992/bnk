# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VoucherRule(models.Model):
    _name = 'voucher.rule'
    _description = "Voucher Rules"

    name = fields.Char(compute='_compute_name', store=True)
    min_quantity = fields.Float(string="Min sale order")
    max_quantity = fields.Float(string="Max sale order")
    rate = fields.Float(string="Voucher rate", required=True)
    voucher_program_id = fields.Many2one('voucher.program', string="Voucher Program", ondelete='cascade')

    def check_rule(self, val):
        if val > self.min_quantity and val < self.max_quantity:
            return True
        return False

    @api.constrains('rate')
    def _check_rate(self):
        for record in self:
            if record.rate == 0:
                raise ValidationError('Invalid voucher rate!')
            if record.rate < 0:
                raise ValidationError('Invalid voucher rate!')

    @api.constrains('min_quantity', 'max_quantity')
    def _check_rule_quantity(self):
        for record in self:
            if record.max_quantity != 0:
                if record.min_quantity > record.max_quantity:
                    raise ValidationError('Max_quantity should be greater than min_quantity')

    @api.constrains('min_quantity')
    def _check_min_quantity(self):
        for record in self:
            if record.min_quantity != 0:
                if record.min_quantity < 0:
                    raise ValidationError('Min_quantity should be greater than 0')

    @api.constrains('max_quantity')
    def _check_max_quantity(self):
        for record in self:
            if record.max_quantity != 0:
                if record.max_quantity < 0:
                    raise ValidationError('Max_quantity should be greater than 0')

    @api.depends('min_quantity', 'max_quantity')
    def _compute_name(self):
        for record in self:
            if record.min_quantity == 0:
                record.name = 'Total saleorder =< %s' %(record.max_quantity,)
            elif record.max_quantity == 0:
                record.name = 'Total saleorder > %s' %(record.min_quantity,)
            else:
                record.name = '%s < Total saleorder =< %s' %(record.min_quantity, record.max_quantity)
        return record.name

            