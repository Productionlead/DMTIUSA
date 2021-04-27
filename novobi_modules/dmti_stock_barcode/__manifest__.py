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
    'name': 'DMTI: Stock Barcode',
    'version': '1.0',
    'summary': '',
    'author': 'Novobi LLC',
    'depends': [
        'product', 'stock_barcode'
    ],
    'data': [
        'views/assets.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}