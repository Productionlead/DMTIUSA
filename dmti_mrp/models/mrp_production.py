# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    po_id = fields.Many2one('purchase.order', 'Purchase Order')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', '|', ('name', operator, name), ('po_id.name', operator, name), ('product_id', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        res = []
        for field in self:
                res.append((field.id, '{0} - {1} ({2})'.format(field.name, field.po_id.name if field.po_id else '', field.product_id.default_code)))
        return res