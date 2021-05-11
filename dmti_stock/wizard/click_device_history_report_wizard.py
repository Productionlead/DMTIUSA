from odoo import api, fields, models, _
import base64
import xlwt
import itertools
from io import BytesIO
from odoo.exceptions import UserError

class ClickDeviceHistoryReportWizard(models.TransientModel):

    _name = 'click.device.history.report.wizard'
    _description = 'Click Device History Report Wizard'

    product_id = fields.Many2one('product.product', 'Product')
    lot_id = fields.Many2one('stock.production.lot', 'Lot Number')
    customer_id = fields.Many2one('res.partner', 'Customer')
    delivery_id = fields.Many2one('res.partner', 'Delivery Address')
    shipping_date_from = fields.Date('Shipping Date From')
    shipping_date_to = fields.Date('Shipping Date To')
    file = fields.Binary('export file')

    def export_device_history_data(self):
        self.ensure_one()
        domain = [('picking_id.picking_type_code', '=', 'outgoing'), ('picking_id.state', '=', 'done')]
        if self.product_id:
            domain += [('product_id', '=', self.product_id.id)]
        if self.lot_id:
            domain += [('lot_id', '=', self.lot_id.id)]
        if self.customer_id:
            domain += [('picking_id.sale_id.partner_id', '=', self.customer_id.id)]
        if self.delivery_id:
            domain += [('picking_id.partner_id', '=', self.delivery_id.id)]
        if self.shipping_date_from:
            domain += [('picking_id.date_done', '>=', self.shipping_date_from)]
        if self.shipping_date_to:
            domain += [('picking_id.date_done', '<=', self.shipping_date_to)]
        if len(domain) == 2:
            raise UserError("Please select at least one criteria.")
        line_items = self.env['stock.move.line'].sudo().search(domain)
        # generate Exel file
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Device History')
        # add header
        header = ['UDI', 'HIBC', 'Part Number', 'Product Name', 'Finished Good Lot Number', 'Sterilization Lot Number',
                  'Finished Good Quantity', 'Ship To / Customer Name', 'Ship To / Contact Name', 'Street Address 1',
                  'Street Address 2', 'City', 'State', 'Zip', 'Ship Date'
                ]
        col_width = 256 * 20  # 20 characters wide
        for col in range(len(header)):
            worksheet.write(0, col, header[col])
        try:
            for i in itertools.count():
                worksheet.col(i).width = col_width
        except ValueError:
            pass
        # add data
        for row in range(1, len(line_items)+1):
            line = line_items[row-1]
            product_id = line.product_id
            shipping_date = line.picking_id.date_done or line.picking_id.scheduled_date or ""
            worksheet.write(row, 0, product_id.dmti_udi or "")
            worksheet.write(row, 1, product_id.dmti_hibc or "")
            worksheet.write(row, 2, product_id.default_code or "")
            worksheet.write(row, 3, product_id.name or "")
            worksheet.write(row, 4, line.lot_id.name or "")
            worksheet.write(row, 5, line.lot_id.ref or "")
            worksheet.write(row, 6, line.qty_done or "")
            worksheet.write(row, 7, line.picking_id.sale_id.partner_id.name or "")
            worksheet.write(row, 8, line.picking_id.partner_id.name or "")
            worksheet.write(row, 9, line.picking_id.partner_id.street or "")
            worksheet.write(row, 10, line.picking_id.partner_id.street2 or "")
            worksheet.write(row, 11, line.picking_id.partner_id.city or "")
            worksheet.write(row, 12, line.picking_id.partner_id.state_id.name or "")
            worksheet.write(row, 13, line.picking_id.partner_id.zip or "")
            worksheet.write(row, 14, str(shipping_date))
        # save
        buffer = BytesIO()
        workbook.save(buffer)
        self.file = base64.encodebytes(buffer.getvalue())
        value = dict(
            type='ir.actions.act_url',
            target='new',
            url='/web/content?model=%s&id=%s&field=file&download=true&filename=DeviceHistoryReport.xls' % (self._name, self.id),
        )
        return value