from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    dmti_udi = fields.Char(string="DI(UDI)")
    dmti_hibc = fields.Char(string="DI(HIBC)")
