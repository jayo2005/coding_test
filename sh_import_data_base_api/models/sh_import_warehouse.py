
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"

    def process_warehouse_data(self,data):
        ''' ======== Prepare warehouse data dict ========= '''
        warehouse_vals = {
            'remote_warehouse_id':data.get('id'),
            'name' : data.get('name'),  
            'code':data.get('code'),
            'reception_steps':data.get('reception_steps').get('sh_api_current_state'),
            'delivery_steps':data.get('delivery_steps').get('sh_api_current_state'),
        }       
        if data.get('lot_stock_id'):
            lot_stock_id=self.env['stock.location'].search([('remote_location_id','=',data.get('lot_stock_id').get('id'))],limit=1)
            if lot_stock_id:
                warehouse_vals['lot_stock_id']=lot_stock_id.id
            else:
                location_vals=self.process_location_data(data.get('lot_stock_id'))
                lot_stock_id=self.env['stock.location'].create(location_vals)
                if data.get('lot_stock_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('lot_stock_id').get('location_id').get('id'))],limit=1)
                    lot_stock_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['lot_stock_id']=lot_stock_id.id
        if data.get('view_location_id'):
            view_location_id=self.env['stock.location'].search([('remote_location_id','=',data.get('view_location_id').get('id'))],limit=1)
            if view_location_id:
                warehouse_vals['view_location_id']=view_location_id.id
            else:
                location_vals=self.process_location_data(data.get('view_location_id'))
                view_location_id=self.env['stock.location'].create(location_vals)
                if data.get('view_location_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('view_location_id').get('location_id').get('id'))],limit=1)
                    view_location_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['view_location_id']=view_location_id.id
        if data.get('wh_input_stock_loc_id'):
            wh_input_stock_loc_id=self.env['stock.location'].search([('remote_location_id','=',data.get('wh_input_stock_loc_id').get('id'))],limit=1)
            if wh_input_stock_loc_id:
                warehouse_vals['wh_input_stock_loc_id']=wh_input_stock_loc_id.id
            else:
                location_vals=self.process_location_data(data.get('wh_input_stock_loc_id'))
                wh_input_stock_loc_id=self.env['stock.location'].create(location_vals)
                if data.get('wh_input_stock_loc_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('wh_input_stock_loc_id').get('location_id').get('id'))],limit=1)
                    wh_input_stock_loc_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['wh_input_stock_loc_id']=wh_input_stock_loc_id.id
        if data.get('wh_output_stock_loc_id'):
            wh_output_stock_loc_id=self.env['stock.location'].search([('remote_location_id','=',data.get('wh_output_stock_loc_id').get('id'))],limit=1)
            if wh_output_stock_loc_id:
                warehouse_vals['wh_output_stock_loc_id']=wh_output_stock_loc_id.id
            else:
                location_vals=self.process_location_data(data.get('wh_output_stock_loc_id'))
                wh_output_stock_loc_id=self.env['stock.location'].create(location_vals)
                if data.get('wh_output_stock_loc_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('wh_output_stock_loc_id').get('location_id').get('id'))],limit=1)
                    wh_output_stock_loc_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['wh_output_stock_loc_id']=wh_output_stock_loc_id.id
        if data.get('wh_pack_stock_loc_id'):
            wh_pack_stock_loc_id=self.env['stock.location'].search([('remote_location_id','=',data.get('wh_pack_stock_loc_id').get('id'))],limit=1)
            if wh_pack_stock_loc_id:
                warehouse_vals['wh_pack_stock_loc_id']=wh_pack_stock_loc_id.id
            else:
                location_vals=self.process_location_data(data.get('wh_pack_stock_loc_id'))
                wh_pack_stock_loc_id=self.env['stock.location'].create(location_vals)
                if data.get('wh_pack_stock_loc_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('wh_pack_stock_loc_id').get('location_id').get('id'))],limit=1)
                    wh_pack_stock_loc_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['wh_pack_stock_loc_id']=wh_pack_stock_loc_id.id
        if data.get('wh_qc_stock_loc_id'):
            wh_qc_stock_loc_id=self.env['stock.location'].search([('remote_location_id','=',data.get('wh_qc_stock_loc_id').get('id'))],limit=1)
            if wh_qc_stock_loc_id:
                warehouse_vals['wh_qc_stock_loc_id']=wh_qc_stock_loc_id.id
            else:
                location_vals=self.process_location_data(data.get('wh_qc_stock_loc_id'))
                wh_qc_stock_loc_id=self.env['stock.location'].create(location_vals)
                if data.get('wh_qc_stock_loc_id'):
                    already_parent_location = self.env['stock.location'].search([('remote_location_id','=',data.get('wh_qc_stock_loc_id').get('location_id').get('id'))],limit=1)
                    wh_qc_stock_loc_id.write({
                        'location_id':already_parent_location.id,
                    })
                warehouse_vals['wh_qc_stock_loc_id']=wh_qc_stock_loc_id.id
        return warehouse_vals
    
    def import_warehouses(self):
        ''' ============== Import Warehouse ====================== '''
        response = requests.get('%s/api/public/stock.warehouse?query={id,name,code,delivery_steps,reception_steps,lot_stock_id{*}}' %(self.base_url))
        if response.status_code == 200:
            response_json = response.json()
            total_count = response_json['count']
            count=0
            for warehouse in response_json['result']:
                domain_by_id=['|',('remote_warehouse_id','=',warehouse.get('id')),('name', '=', warehouse.get('name'))]
                domain_by_code=[('code','=',warehouse.get('code'))]
                already_warehouse_by_id = self.env['stock.warehouse'].search(domain_by_id,limit=1)
                already_warehouse_by_code = self.env['stock.warehouse'].search(domain_by_code,limit=1)
                warehouse_data=self.process_warehouse_data(warehouse)
                if already_warehouse_by_id:
                    already_warehouse_by_id.write(warehouse_data)
                elif already_warehouse_by_code:
                    already_warehouse_by_code.write(warehouse_data)
                else:
                    self.env['stock.warehouse'].create(warehouse_data)
                count += 1    
            if count == total_count:
                vals = {
                    "name": self.name,
                    "state": "success",
                    "field_type": "warehouse",
                    "error": "Warehouse Imported Successfully",
                    "datetime": datetime.now(),
                    "base_config_id": self.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)
        else:
            vals = {
                "name": self.name,
                "state": "error",
                "field_type": "warehouse",
                "error": response.text,
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)
    