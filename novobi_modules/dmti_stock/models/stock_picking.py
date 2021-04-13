from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'stock.picking'
    back_order_note_id = fields.Many2one('back.order.note', string='Back Order Note')
    back_order_message = fields.Char()

    @api.onchange('back_order_note_id')
    def _onchange_back_order_note_id(self):
        for picking in self:
            if picking.back_order_note_id:
                picking.back_order_message = picking.back_order_note_id.name