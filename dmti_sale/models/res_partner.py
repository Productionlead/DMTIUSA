from odoo import api, fields, models, tools, _
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'
    has_w9_document = fields.Boolean(string="Has W9 on File", default=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        partner_ids = list(super(ResPartner, self)._name_search(name, args, operator, limit, name_get_uid))
        domain = ['|', '|', '|', ('street', operator, name), ('street2', operator, name), ('city', operator, name), ('zip', operator, name)]
        partners = list(self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid))
        return list(set(partner_ids + partners))