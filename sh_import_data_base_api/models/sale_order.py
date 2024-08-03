# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    remote_order_id = fields.Char("Remote Order ID")
    
    delivery_state = fields.Selection(
        [
            ("no", "No Delivery"),
            ("unprocessed", "Unprocessed"),
            ("partially", "Partially Delivered"),
            ("done", "Delivered"),
        ],
        # Compute method have a different name then the field because
        # the method _compute_delivery_state already exist to compute
        # the field delivery_set
        compute="_compute_sale_delivery_state",
        store=False,
    )
    
    
    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            connected_invoice=self.env['account.move'].search([('invoice_origin','=',order.name)])
            order.invoice_ids = invoices+connected_invoice
            order.invoice_count = len(order.invoice_ids)
    
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    remote_order_line_id = fields.Char("Remote Order line ID")

    delivery_state = fields.Selection(
        [
            ("no", "No delivery"),
            ("unprocessed", "Unprocessed"),
            ("partially", "Partially"),
            ("done", "Delivered"),
        ],
        # Compute method have a different name then the field because
        # the method _compute_delivery_state already exist to compute
        # the field delivery_set in odoo delivery module
        compute="_compute_sale_line_delivery_state",
        store=False,
    )
