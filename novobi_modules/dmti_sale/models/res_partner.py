from odoo import api, fields, models, tools, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    has_w9_document = fields.Boolean(string="Has W9?", default=False)