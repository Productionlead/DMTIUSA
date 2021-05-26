from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Override
    ref = fields.Char(string='Customer PO')
