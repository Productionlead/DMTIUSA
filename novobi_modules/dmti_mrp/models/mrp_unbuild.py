# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression

class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    @api.onchange('mo_id')
    def _onchange_subcontracting_mo(self):
        if self.mo_id and self.mo_id.po_id:
            finished_good_location_id = self.mo_id.location_dest_id
            self.update({
                'location_id': finished_good_location_id,
                'location_dest_id': finished_good_location_id
            })
