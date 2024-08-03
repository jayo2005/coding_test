# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    remote_product_category_id = fields.Char("Remote Product Category ID")