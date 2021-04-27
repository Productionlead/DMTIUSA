from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    back_order_note_id = fields.Many2one('back.order.note', string='Back Order Note')
    back_order_message = fields.Char()

    @api.onchange('back_order_note_id')
    def _onchange_back_order_note_id(self):
        for picking in self:
            if picking.back_order_note_id:
                picking.back_order_message = picking.back_order_note_id.name

    @api.model
    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        vals = super(StockPicking, self)._prepare_subcontract_mo_vals(subcontract_move, bom)
        if self.purchase_id:
            vals.update({
                'po_id': self.purchase_id.id
            })
        return vals