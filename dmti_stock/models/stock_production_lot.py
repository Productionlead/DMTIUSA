# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression
from odoo.exceptions import UserError

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    ref = fields.Char('Sterilization Lot Number', help="Internal reference number in case it differs from the manufacturer's lot/serial number")
    dmti_udi_hibc_code = fields.Char('UDI/HIBC')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('ref', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    # def write(self, vals):
    #     if vals.get('dmti_udi_hibc_code', False):
    #         stock_move_line_id = self.env['stock.move.line'].search([('lot_name', '=', self.name), ('product_id', '=', self.product_id.id), ('dmti_udi_hibc_code', '!=', vals.get('dmti_udi_hibc_code'))], limit=1)
    #         if stock_move_line_id:
    #             raise UserError("UDI/HIBC must be same as UDI/HIBC on Lot Number.")
    #     return super(StockProductionLot, self).write(vals)