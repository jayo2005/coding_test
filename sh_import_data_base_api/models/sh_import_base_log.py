# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ImportLogger(models.Model):
    _name = 'sh.import.base.log'
    _description = 'Helps you to maintain the activity done'
    _order = 'id desc'
     
    name = fields.Char("Name")
    error = fields.Char("Message")
    datetime = fields.Datetime("Date & Time")
    base_config_id = fields.Many2one('sh.import.base')
    field_type = fields.Selection([('customer','Customer'),('product','Product'),
    ('category','Product Category'),('auth','Authentication'),('uom','Unit of Measure'),
    ('order','Sale order'),('location','Location'),('warehouse','Warehouse'),('payment','Payment'),('invoice','Invoice')],string="Import Type")
    state = fields.Selection([('success','Success'),('error','Failed')])
    operation = fields.Selection([('import','Import'),('export','Export')])