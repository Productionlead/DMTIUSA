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
    'name': 'DMTI: MRP',
    'version': '1.0',
    'summary': '',
    'author': 'Novobi LLC',
    'depends': [
        'mrp'
    ],
    'data': [
        'views/mrp_production_tree_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}