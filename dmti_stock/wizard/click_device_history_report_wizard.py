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
    dmti_udi_hibc_code = fields.Char('UDI/HIBC')
    file = fields.Binary('export file')

    def group_line(self, lines):
        results = []
        for line in lines:
            if results and list(filter(lambda x: x[0].product_id.id == line.product_id.id, results)):
                continue
            else:
                group = list(filter(lambda l: l.product_id.id == line.product_id.id, lines))
                results.append(group)
        return results

    def export_device_history_data(self):
        '''
        :return: This function is used to write Finish good products are delivered with their components in file Excel
        '''
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
        if self.dmti_udi_hibc_code:
            domain += ['|', ('dmti_udi_hibc_code', '=', self.dmti_udi_hibc_code), ('lot_id.dmti_udi_hibc_code', '=', self.dmti_udi_hibc_code)]
        if self.shipping_date_from:
            domain += [('picking_id.date_done', '>=', self.shipping_date_from)]
        if self.shipping_date_to:
            domain += [('picking_id.date_done', '<=', self.shipping_date_to)]
        if len(domain) == 2:
            raise UserError("Please select at least one criteria.")
        line_items = self.env['stock.move.line'].sudo().search(domain)
        # Generate Exel file
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Device History')
        # Add header
        header = ['UDI/HIBC', 'Part Number', 'Product Name', 'Finished Good Lot Number', 'Sterilization Lot Number',
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
        # Add data
        max_column = 0
        max_row = 1
        '''
            check_line_lst: If the remaining qty of move line == 0 => add move line in check_line_lst
            max_column: is the largest number of Column
            max_row: is the largest number of Row
            check_lot_list: save list of lot number with quantity of Parent product
        '''
        check_line_lst = []
        check_qty_done_lst = []
        for row in range(1, len(line_items)+1):
            rows = max_row
            column_size = 14
            i = 1
            line = line_items[row-1]
            product_id = line.product_id
            shipping_date = line.picking_id.date_done or line.picking_id.scheduled_date or ""
            partner_id = line.picking_id.partner_id
            customer_id = line.picking_id.sale_id.partner_id
            row_values = [line.dmti_udi_hibc_code or line.lot_id.dmti_udi_hibc_code, product_id.default_code,
                          product_id.name, line.lot_id.name, line.lot_id.ref, line.qty_done,
                          customer_id.name, partner_id.name, partner_id.street, partner_id.street2,
                          partner_id.city, partner_id.state_id.name, partner_id.zip, str(shipping_date)
            ]
            for index, value in enumerate(row_values):
                worksheet.write(max_row, index, value or "")
            lines = self.get_lines(line)
            list_group_lines = self.group_line(lines)
            check_lot_list = [(line.lot_id.id, line.qty_done)]
            max_row = max_row + 1 if not list_group_lines else max_row
            for group_line in list_group_lines:
                qty_need_done = 0
                rows1 = rows
                for index, line_item in enumerate(group_line):
                    if list(filter(lambda l: l.id == line_item.id, check_line_lst)):
                        continue
                    check_qty_done = list(filter(lambda q: q[0] == line_item.id, check_qty_done_lst))
                    if check_qty_done:
                        line_qty_done = check_qty_done[-1][1]
                        if line_qty_done == 0:
                            continue
                    else:
                        line_qty_done = line_item.qty_done
                    component_qty = 0
                    product_qty = 1
                    lot_finish_good_id = None
                    if line_item.production_id:
                        bom_id = line_item.production_id.bom_id
                        lot_finish_good_id = line_item.production_id.lot_producing_id.id
                        if bom_id:
                            product_qty = bom_id.product_qty
                            component = bom_id.bom_line_ids.filtered(lambda l: l.product_id.id == line_item.product_id.id)
                            component_qty = component[0].product_qty if component else 0
                    worksheet.write(0, column_size, "Component Product Name " + str(i) + " (Description)") if i > max_column and index == 0 else None
                    worksheet.write(rows1, column_size, line_item.product_id.display_name)
                    worksheet.write(0, column_size + 1, "Component Lot Number " + str(i)) if i > max_column and index == 0 else None
                    worksheet.write(rows1, column_size + 1, line_item.lot_id.name if line_item.lot_id else '')
                    worksheet.write(0, column_size + 2, "Component Part " + str(i) + " Quantity") if i > max_column and index == 0 else None
                    parent_products = list(filter(lambda x: x[0] == lot_finish_good_id, check_lot_list))
                    if parent_products:
                        parent_quantity_done = parent_products[0][1]
                    else:
                        parent_quantity_done = 0
                    if not qty_need_done:
                        qty_need_done = parent_quantity_done * component_qty / product_qty
                    if qty_need_done <= line_qty_done:
                        qty_done = qty_need_done
                        check_qty_done_lst.append((line_item.id, line_qty_done - qty_need_done))
                        qty_need_done = 0
                    else:
                        check_qty_done_lst.append((line_item.id, 0))
                        qty_done = line_qty_done
                        qty_need_done -= qty_done
                        check_line_lst.append(line_item)
                    worksheet.write(rows1, column_size + 2, qty_done)
                    check_lot_list.append((line_item.lot_id.id, qty_done))
                    rows1 += 1
                    if qty_need_done == 0 and not list(filter(lambda l: l.lot_id.id == line_item.lot_id.id, group_line[index+1:])):
                        break
                if rows1 > max_row:
                    max_row = rows1
                column_size += 3
                i += 1
            if i > max_column:
                max_column = i - 1
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

    @api.model
    def get_lines(self, move_line_id):
        '''
        :param move_line_id: is Finish Good
        :return: component move line of Finish Good that we need to show in file Excel
        '''
        lines = self.env['stock.move.line'].search([
            ('product_id', '=', move_line_id.product_id.id),
            ('lot_id', '=', move_line_id.lot_id.id),
            ('id', '!=', move_line_id.id),
            ('state', '=', 'done'),
        ])
        # Component move lines is stock move lines( component of Fish Good) with picking type not as "Outgoing"
        component_move_lines = lines.filtered(lambda l: not l.production_id)
        component_move_lines_lst = [move_line_id] + self._lines(move_lines=component_move_lines) if move_line_id.picking_code != 'outgoing' else self._lines(move_lines=component_move_lines)
        return component_move_lines_lst

    @api.model
    def _lines(self, move_lines=[]):
        final_vals = []
        lines = move_lines or []
        for line in lines:
            # Not check for type of move line as Outgoing
            if line.picking_code == 'outgoing':
                continue
            # Finish good( Production)
            elif line.move_id.production_id:
                # Find Component
                if line.consume_line_ids:
                    for line_id in line.consume_line_ids:
                        final_vals += self.get_lines(line_id)
        return final_vals