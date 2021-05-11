from odoo import api, fields, models, tools, _
from odoo.osv import expression

class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_all_products_by_barcode(self):
        res = super(Product, self).get_all_products_by_barcode()
        udi_products = self.env['product.product'].search_read(
            [('dmti_udi', '!=', None), ('type', '!=', 'service')],
            ['dmti_udi', 'display_name', 'uom_id', 'tracking']
        )
        hibc_products = self.env['product.product'].search_read(
            [('dmti_hibc', '!=', None), ('type', '!=', 'service')],
            ['dmti_hibc', 'display_name', 'uom_id', 'tracking']
        )
        udi_products_dict = {product.pop('dmti_udi'): product for product in udi_products}
        hibc_products_dict = {product.pop('dmti_hibc'): product for product in hibc_products}
        products = {**res, **udi_products_dict, **hibc_products_dict}
        return products

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        product_ids = list(super(Product, self)._name_search(name, args, operator, limit, name_get_uid))
        domain = ['|', ('dmti_udi', operator, name), ('dmti_hibc', operator, name)]
        products = list(self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid))
        return list(set(product_ids + products))