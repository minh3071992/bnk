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
    has_voucher = fieldsBoolean('Has voucher?', default='_compute_has_voucher')
