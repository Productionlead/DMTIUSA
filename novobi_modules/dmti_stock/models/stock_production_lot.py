# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('ref', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)