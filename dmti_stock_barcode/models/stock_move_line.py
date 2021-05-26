from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    dmti_udi_hibc_code = fields.Char('UDI/HIBC')

    def _assign_production_lot(self, lot):
        res = super(StockMoveLine, self)._assign_production_lot(lot)
        lot.write({
            'dmti_udi_hibc_code': self.dmti_udi_hibc_code
        })
        return res

    @api.model
    def create(self, vals):
        if vals.get('lot_name', False) and vals.get('product_id', False):
            lot_id = self.env['stock.production.lot'].search([('name', '=', vals.get('lot_name')), ('product_id', '=', vals.get('product_id'))])
            if lot_id and lot_id.dmti_udi_hibc_code != vals.get('dmti_udi_hibc_code', ''):
                raise UserError("UDI/HIBC must be same as UDI/HIBC on Lot Number.")
        return super(StockMoveLine, self).create(vals)