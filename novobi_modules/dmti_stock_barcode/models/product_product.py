from odoo import api, fields, models, tools, _

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