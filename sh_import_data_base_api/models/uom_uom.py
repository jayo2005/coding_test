# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class UomUom(models.Model):
    _inherit = 'uom.uom'

    remote_uom_id = fields.Char("Remote Unit ID")

class UomCategory(models.Model):
    _inherit = 'uom.category'

    remote_uom_category_id = fields.Char("Remote Category Id")