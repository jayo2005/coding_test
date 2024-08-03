# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ImportFailed(models.Model):
    _name = 'sh.import.failed'
    _description = 'Helps you to maintain the failed records track'
    _order = 'id desc'
     
    name = fields.Char("Name")
    error = fields.Char("Message")
    import_json = fields.Char("Import Json")
    datetime = fields.Datetime("Date & Time")
    base_config_id = fields.Many2one('sh.import.base')
    field_type = fields.Selection([('customer','Customer'),('product','Product'),
    ('category','Product Category'),('auth','Authentication'),('order','Sale order'),
    ('location','Location'),('warehouse','Warehouse'),('payment','Payment'),('invoice','Invoice')],string="Import Type")
