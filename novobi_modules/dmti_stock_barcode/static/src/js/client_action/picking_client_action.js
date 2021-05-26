odoo.define('dmti_stock_barcode.picking_client_action', function (require) {
"use strict";
var PickingClientAction = require('stock_barcode.picking_client_action');
PickingClientAction.include({
    _createLineCommand: function (line) {
        return [0, 0, {
            picking_id: line.picking_id,
            product_id:  line.product_id.id,
            product_uom_id: line.product_uom_id[0],
            qty_done: line.qty_done,
            location_id: line.location_id.id,
            location_dest_id: line.location_dest_id.id,
            lot_name: line.lot_name,
            lot_id: line.lot_id && line.lot_id[0],
            state: 'assigned',
            owner_id: line.owner_id && line.owner_id[0],
            package_id: line.package_id ? line.package_id[0] : false,
            result_package_id: line.result_package_id ? line.result_package_id[0] : false,
            dummy_id: line.virtual_id,
            dmti_udi_hibc_code: line.dmti_udi_hibc_code,
        }];
    },
    _makeNewLine: function (params) {
        var virtualId = this._getNewVirtualId();
        var currentPage = this.pages[this.currentPageIndex];
        var newLine = {
            'picking_id': this.currentState.id,
            'product_id': {
                'id': params.product.id,
                'display_name': params.product.display_name,
                'barcode': params.barcode,
                'tracking': params.product.tracking,
            },
            'product_barcode': params.barcode,
            'display_name': params.product.display_name,
            'product_uom_qty': 0,
            'product_uom_id': params.product.uom_id,
            'qty_done': params.qty_done,
            'location_id': {
                'id': currentPage.location_id,
                'display_name': currentPage.location_name,
            },
            'location_dest_id': {
                'id': currentPage.location_dest_id,
                'display_name': currentPage.location_dest_name,
            },
            'package_id': params.package_id,
            'result_package_id': params.result_package_id,
            'owner_id': params.owner_id,
            'state': 'assigned',
            'reference': this.name,
            'virtual_id': virtualId,
            'dmti_udi_hibc_code': params.dmti_udi_hibc_code,
        };
        return newLine;
    },
})
});