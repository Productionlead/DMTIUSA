# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BackOrderNote(models.Model):
    _name = "back.order.note"
    _description = "Back Order Note"

    name = fields.Char(string='Name', required=True)