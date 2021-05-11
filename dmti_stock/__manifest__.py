# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################


{
    'name': 'DMTI: Stock',
    'version': '1.0',
    'summary': '',
    'author': 'Novobi LLC',
    'depends': [
        'stock', 'mrp_subcontracting'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'report/report_deliveryslip.xml',
        'report/report_device_history.xml',
        'report/device_history_template.xml',
        'wizard/click_device_history_report_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}