# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    remote_picking_id = fields.Char("Remote Picking ID")
    
    def action_picking_draft(self):
        for rec in self:
            if rec.sudo().mapped('move_ids_without_package'):
                rec._sh_unreseve_qty()
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})

                # cancel related accouting entries
                account_move = rec.sudo().mapped(
                    'move_ids_without_package').sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(
                    ['|', ('credit_move_id', 'in', reconcile_ids), ('debit_move_id', 'in', reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped(
                    'line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state': 'draft', 'name': '/'})
                account_move.sudo().with_context(
                    {'force_delete': True}).unlink()
                    
                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped(
                    'move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

            rec.sudo().write({'state': 'draft'})
    
    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_ids_without_package').mapped('move_line_ids'):
            
            # Check qty is not in draft and cancel state
            if self.state not in ['draft','cancel','assigned','waiting'] :
                
                # unreserve qty
                quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                               ('product_id', '=',
                                                                move_line.product_id.id),
                                                               ('lot_id', '=', move_line.lot_id.id)], limit=1)
    
                if quant:
                    quant.write({'quantity': quant.quantity + move_line.qty_done})
    
                quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                               ('product_id', '=',
                                                                move_line.product_id.id),
                                                               ('lot_id', '=', move_line.lot_id.id)], limit=1)
    
                if quant:
                    quant.write({'quantity': quant.quantity - move_line.qty_done})
    
    

class StockMove(models.Model):
    _inherit = 'stock.move'

    remote_move_id = fields.Char("Remote Move ID")
    
