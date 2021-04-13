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
    'name': 'DMTI: Sale',
    'version': '1.0',
    'summary': '',
    'author': 'Novobi LLC',
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/back_order_note.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}