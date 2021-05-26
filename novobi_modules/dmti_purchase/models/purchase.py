from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Override
    partner_ref = fields.Char(string='Customer PO')
