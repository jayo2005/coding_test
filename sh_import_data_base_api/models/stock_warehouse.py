# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    remote_warehouse_id = fields.Char("Remote warehouse ID")