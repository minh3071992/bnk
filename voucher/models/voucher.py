# -*- coding: utf-8 -*-

import random
from odoo import api, fields, models

class Voucher(models.Model):
    _name = 'voucher.voucher'
    _description = "Voucher code"

    @api.model
    def _generate_code(self):
        return str(random.getrandbits(64))

    name = fields.Char(default=_generate_code, required=True, readonly=True)
    voucher_program_id = fields.Many2one('voucher.program', string="Voucher program", ondelete="set null", readonly=True)
    expiration_date = fields.Datetime(related='voucher_program_id.expiration_date')
    partner_id = fields.Many2one('res.partner', string='Voucher owner', ondelete="cascade", readonly=True)
    value = fields.Float(string="Voucher value", readonly=True)
    state = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('expired', 'Expired')
    ], required=True, default='ongoing')
