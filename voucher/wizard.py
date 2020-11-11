# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class Wizard(models.TransientModel):
    _name = 'voucher.wizard'
    _description = "Report Voucher Program"

    def _default_voucher_program(self):
        return self.env['voucher.program'].browse([self._context.get('active_id')])

    voucher_program_id = fields.Many2one('voucher.program', string="Voucher Program", required=True, default=_default_voucher_program)
    
