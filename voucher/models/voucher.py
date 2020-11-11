# -*- coding: utf-8 -*-

import random
from odoo import api, fields, models

class Voucher(models.Model):
    _name = 'voucher.voucher'
    _decription = "Voucher code"

    @api.model
    def _generate_code(self):
        return str(random.getrandbits(64))

    name = fields.Char(default=_generate_code, required=True, readonly=True)
    voucher_program_id = fields.Many2one('voucher.program', string="Voucher program", ondelete="cascade")
    expiration_date = fields.Datetime(related='voucher_program_id.expiration_date')
    partner_id = fields.Many2one('res.partner', string='Voucher owner', ondelete="cascade")
    currency_id = fields.Many2one('res.currency', string="Currency")
    value = fields.Monetary(string="Voucher value")
