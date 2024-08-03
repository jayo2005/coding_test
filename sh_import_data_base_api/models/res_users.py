# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    remote_user_id = fields.Char("Remote User ID")