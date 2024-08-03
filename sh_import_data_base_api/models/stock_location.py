# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    remote_location_id = fields.Char("Remote Location ID")