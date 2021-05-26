odoo.define('dmti_stock_barcode.ClientAction', function (require) {
"use strict";
var core = require('web.core');
var ClientAction = require('stock_barcode.ClientAction');
ClientAction.include({
    _isProduct: function (barcode) {
        if (barcode[0] == '('){
            // It is UDI code
            var pos = barcode.indexOf("(10)");
            if (pos != -1){
                var lot_str = barcode.substring(pos+4, barcode.length);
                var lot_number = lot_str.substring(0, lot_str.indexOf("("));
            }
            barcode = barcode.substring(4, 18);
        }else if(barcode[0] == '+'){
            // It is HIBC code
            var pos = barcode.indexOf("/$$8017");
            var lot_str = barcode.substring(pos+7, barcode.length);
            var lot_number = lot_str.substring(0, lot_str.indexOf("/"));
            barcode = barcode.substring(1, pos);
        }
        var parsed = this.barcodeParser.parse_barcode(barcode);
        if (parsed.type === 'weight') {
            var product = this.productsByBarcode[parsed.base_code];
            // if base barcode is not a product, error will be thrown in _step_product()
            if (product) {
                product.qty = parsed.value;
            }
            return product;
        } else {
            return {'product': this.productsByBarcode[parsed.code], 'lot_number': lot_number , 'dmti_udi_hibc_code': barcode}
        }
    },
    _step_product: function (barcode, linesActions) {
        var self = this;
        this.currentStep = 'product';
        this.stepState = $.extend(true, {}, this.currentState);
        var errorMessage;

        var result = this._isProduct(barcode);
        var product = result['product'];
        var lot_name = result['lot_number'];
        var dmti_udi_hibc_code = result['dmti_udi_hibc_code']
        if (product) {
            if (product.tracking !== 'none' && self.requireLotNumber) {
                this.currentStep = 'lot';
            }
            var res = this._incrementLines({'product': product, 'barcode': barcode, 'lot_name': lot_name, 'dmti_udi_hibc_code': dmti_udi_hibc_code});
            if (res.isNewLine) {
                if (this.actionParams.model === 'stock.inventory') {
                    // FIXME sle: add owner_id, prod_lot_id, owner_id, product_uom_id
                    return this._rpc({
                        model: 'product.product',
                        method: 'get_theoretical_quantity',
                        args: [
                            res.lineDescription.product_id.id,
                            res.lineDescription.location_id.id,
                        ],
                    }).then(function (theoretical_qty) {
                        res.lineDescription.theoretical_qty = theoretical_qty;
                        linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                        self.scannedLines.push(res.id || res.virtualId);
                        return Promise.resolve({linesActions: linesActions});
                    });
                } else {
                    linesActions.push([this.linesWidget.addProduct, [res.lineDescription, this.actionParams.model]]);
                }
            } else if (!(res.id || res.virtualId)) {
                return Promise.reject(_("There are no lines to increment."));
            } else {
                if (product.tracking === 'none' || !self.requireLotNumber) {
                    linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, product.qty || 1, this.actionParams.model]]);
                } else {
                    linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, 0, this.actionParams.model]]);
                }
            }
            this.scannedLines.push(res.id || res.virtualId);
            return Promise.resolve({linesActions: linesActions});
        } else {
            var success = function (res) {
                return Promise.resolve({linesActions: res.linesActions});
            };
            var fail = function (specializedErrorMessage) {
                self.currentStep = 'product';
                if (specializedErrorMessage){
                    return Promise.reject(specializedErrorMessage);
                }
                if (! self.scannedLines.length) {
                    if (self.groups.group_tracking_lot) {
                        errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
                    } else {
                        errorMessage = _t('You are expected to scan one or more products.');
                    }
                    return Promise.reject(errorMessage);
                }

                var destinationLocation = self.locationsByBarcode[barcode];
                if (destinationLocation) {
                    return self._step_destination(barcode, linesActions);
                } else {
                    errorMessage = _t('You are expected to scan more products or a destination location.');
                    return Promise.reject(errorMessage);
                }
            };
            return self._step_lot(barcode, linesActions).then(success, function () {
                return self._step_package(barcode, linesActions).then(success, fail);
            });
        }
    },
    _incrementLines: function (params) {
        var lot_name = params.lot_name;
        if (lot_name){
            var udi_pos = lot_name.indexOf("(10)");
            var hibc_pos = lot_name.indexOf("/$$8017");
            if (udi_pos != -1){
                var lot_str = lot_name.substring(udi_pos+4, lot_name.length);
                var lot_number = lot_str.substring(0, lot_str.indexOf("("));
                params.lot_name = lot_number;
            }else if(hibc_pos != -1){
                var lot_str = lot_name.substring(hibc_pos+7, lot_name.length);
                var lot_number = lot_str.substring(0, lot_str.indexOf("/"));
                params.lot_name = lot_number;
            }
        }
        var line = this._findCandidateLineToIncrement(params);
        var isNewLine = false;
        if (line) {
            // Update the line with the processed quantity.
            if (params.product.tracking === 'none' ||
                params.lot_id ||
                params.lot_name ||
                !this.requireLotNumber
                ) {
                if (this._isPickingRelated()) {
                    line.qty_done += params.product.qty || 1;
                    if (params.package_id) {
                        line.package_id = params.package_id;
                    }
                    if (params.result_package_id) {
                        line.result_package_id = params.result_package_id;
                    }
                } else if (this.actionParams.model === 'stock.inventory') {
                    line.product_qty += params.product.qty || 1;
                }
            }
        } else if (this._isAbleToCreateNewLine()) {
            isNewLine = true;
            // Create a line with the processed quantity.
            if (params.product.tracking === 'none' ||
                params.lot_id ||
                params.lot_name ||
                !this.requireLotNumber
                ) {
                params.qty_done = params.product.qty || 1;
            } else {
                params.qty_done = 0;
            }
            line = this._makeNewLine(params);
            this._getLines(this.currentState).push(line);
            this.pages[this.currentPageIndex].lines.push(line);
        }
        if (this._isPickingRelated()) {
            if (params.lot_id) {
                line.lot_id = [params.lot_id];
            }
            if (params.lot_name) {
                line.lot_name = params.lot_name;
            }
        } else if (this.actionParams.model === 'stock.inventory') {
            if (params.lot_id) {
                line.prod_lot_id = [params.lot_id, params.lot_name];
            }
        }
        return {
            'id': line.id,
            'virtualId': line.virtual_id,
            'lineDescription': line,
            'isNewLine': isNewLine,
        };
    },
})
});