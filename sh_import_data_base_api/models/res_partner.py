# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    remote_partner_id = fields.Char("Remote Partner ID")