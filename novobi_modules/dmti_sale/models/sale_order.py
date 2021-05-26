from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Override
    client_order_ref = fields.Char(string='Customer PO')

    # New fields
    has_w9_document = fields.Boolean(string="Has W9 on File", related="partner_id.has_w9_document")
