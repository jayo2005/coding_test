# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"
    
    def process_stock_move_data(self,data,picking):
        moves_list=[]
        find_empty_id_move=self.env['stock.move'].search([('picking_id.remote_picking_id','=',picking),('remote_move_id','=','')])
        if find_empty_id_move:
            for move in find_empty_id_move:
                move.unlink()      
        for move in data:
            
            move_vals={
                'name':move.get('name'),
                'is_inventory':move.get('is_inventory'),
                'is_locked':move.get('is_locked'),
                'is_quantity_done_editable':move.get('is_quantity_done_editable'),
                'quantity_done':move.get('quantity_done'),
                'product_uom_qty':move.get('product_uom_qty'),
                'price_unit':move.get('price_unit'),
                'state':move.get('state').get('sh_api_current_state'),
                'remote_move_id':move.get('id'),
            }
            if move.get('location_id'):
                location_id=self.env['stock.location'].search([('remote_location_id','=',move.get('location_id'))],limit=1)
                if location_id:
                    move_vals['location_id']= location_id.id
            if move.get('location_dest_id'):
                location_dest_id=self.env['stock.location'].search([('remote_location_id','=',move.get('location_dest_id'))],limit=1)
                if location_dest_id:
                    move_vals['location_dest_id']= location_dest_id.id
            domain = [('remote_product_template_id', '=', move['product_id']['product_tmpl_id']['id'])]
            if move.get('product_id'):
                domain = [('remote_product_template_id', '=', move['product_id']['product_tmpl_id']['id'])]
                find_product = self.env['product.template'].search(domain,limit=1)
                if find_product:
                    find_product_var = self.env['product.product'].search([('product_tmpl_id','=',find_product.id)],limit=1)
                    if find_product_var:
                        move_vals['product_id'] = find_product_var.id
                        move_vals['name'] = find_product_var.display_name
                    else:
                        product_vals=self.process_product_data(move['product_id']['product_tmpl_id'])
                        product_id=self.env['product.template'].create(product_vals)
                        if product_id:
                            find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
                            if find_product_var:

                                move_vals['product_id']=find_product_var.id
                                move_vals['name'] = find_product_var.display_name
                            else:
                                check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
                                move_vals['product_id'] = check_archived_product.id   
                                move_vals['name'] = check_archived_product.display_name
                else:
                    product_vals=self.process_product_data(move['product_id']['product_tmpl_id'])
                    product_id=self.env['product.template'].create(product_vals)
                    if product_id:
                        find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
                        if find_product_var:
                            move_vals['product_id'] = find_product_var.id
                            move_vals['name'] = find_product_var.display_name
                        else:
                            check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
                            move_vals['product_id'] = check_archived_product.id   
                            move_vals['name'] = check_archived_product.display_name
            move_id=self.env['stock.move'].search([('remote_move_id','=',move.get('id'))])
            if move_id:
                if 'quantity_done' in move_vals:
                    del move_vals['quantity_done']
                move_id.write(move_vals)
            else:
                moves_list.append((0,0,move_vals))       
        return moves_list           
                   
                   
    def process_picking_data(self,data,warehouse_id):
        ''' ================= Import Stock Picking =============  '''
        picking_list=[]
        for picking in data:
            picking_vals={
                'remote_picking_id':picking.get('id'),
                'name':picking.get('name'),
                'state':picking.get('state').get('sh_api_current_state'),
                'origin':picking.get('origin')
            }
            if picking.get('date'):
                date_time=datetime.strptime(picking.get('date'),'%Y-%m-%d-%H-%M-%S')
                date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                picking_vals['date']=date_time
            
            if picking.get('date_done'):
                date_time=datetime.strptime(picking.get('date_done'),'%Y-%m-%d-%H-%M-%S')
                date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                picking_vals['date_done']=date_time
                
            # if picking.get('scheduled_date'):
            #     date_time=datetime.strptime(picking.get('scheduled_date'),'%Y-%m-%d-%H-%M-%S')
            #     date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
            #     picking_vals['scheduled_date']=date_time        
            
            # ======== Select Picking type warehouse wise ===========
            if picking.get('picking_type_id'):
                picking_types=self.env['stock.picking.type'].search([
                    ('code','=',picking.get('picking_type_id').get('code').get('sh_api_current_state')),
                    ('warehouse_id.remote_warehouse_id','=',warehouse_id)])
                type_id=False
                for picking_type in picking_types:
                    if picking.get('picking_type_id').get('name') in picking_type.name:
                        type_id=picking_type
                if type_id:
                    picking_vals['picking_type_id']= type_id.id
                    
            # ======== Select Source location from Picking type ===========
            if picking.get('location_id'):
                location_id=self.env['stock.location'].search([('remote_location_id','=',picking.get('location_id'))],limit=1)
                if location_id:
                    picking_vals['location_id']= location_id.id
                    
            # ======== Select Destination location from Picking type ===========
            if picking.get('location_dest_id'):
                location_dest_id=self.env['stock.location'].search([('remote_location_id','=',picking.get('location_dest_id'))],limit=1)
                if location_dest_id:
                    picking_vals['location_dest_id']= location_dest_id.id
                    
            # ======== Get partner if already created or create =====
            
            if picking.get('partner_id'):
                domain = [('remote_partner_id', '=', picking['partner_id']['id'])]
                find_customer = self.env['res.partner'].search(domain)
                if find_customer:
                    picking_vals['partner_id'] = find_customer.id
                else:
                    contact_vals=self.process_contact_data(picking['partner_id'])
                    partner_id=self.env['res.partner'].create(contact_vals)
                    if partner_id:
                        picking_vals['partner_id']=partner_id.id
                        
            # ======== Prepare Moves =====     
            
            if picking.get('move_ids_without_package'):
                moves_list = self.process_stock_move_data(picking.get('move_ids_without_package'),picking.get('id'))
                if moves_list:
                    picking_vals['move_ids_without_package']=moves_list
             
            if picking_vals.get('picking_type_id'):   
                picking_list.append((0,0,picking_vals))  
            
        return picking_list 