
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"

    def process_location_data(self,data):
        ''' ============== Prepare Location dict ====================== '''
        location_vals = {
            'remote_location_id':data.get('id'),
            'comment' : data.get('comment'),  
            'name':data.get('name'),
            'scrap_location':data.get('scrap_location'),
            'return_location':data.get('return_location'),
            'usage':data.get('usage').get('sh_api_current_state'),
        }       
        return location_vals
    
    def import_locations(self):
        ''' ============== Import Locations ====================== '''
        response = requests.get('%s/api/public/stock.location?query={id,child_ids{*},comment,location_id{*},name,parent_path,return_location,scrap_location,usage}' %(self.base_url))
        if response.status_code == 200:
            response_json = response.json()
            count=0
            for location in response_json.get('result'):
                domain=['|',('remote_location_id','=',location.get('id')),('name', '=', location.get('name'))]
                already_location = self.env['stock.location'].search(domain,limit=1)
                location_data=self.process_location_data(location)
                try:
                    if not already_location:
                        self.env['stock.location'].create(location_data)
                    else:
                        already_location.write({
                            'remote_location_id' : location.get('id')
                        })
                    count += 1
                except Exception as e:
                    vals = {
                        "name": location['id'],
                        "error": e,
                        "import_json" : location,
                        "field_type": "location",                           
                        "datetime": datetime.now(),
                        "base_config_id": self.id,
                    }
                    self.env['sh.import.failed'].create(vals)
                
            for location in response_json['result']:
                already_location = self.env['stock.location'].search([('remote_location_id','=',location.get('id'))],limit=1)
                already_parent_location = self.env['stock.location'].search([('remote_location_id','=',location.get('location_id').get('id'))],limit=1)
                try:
                    if already_location and already_parent_location:
                        already_location.write({
                            'location_id':already_parent_location,
                        })
                except Exception as e:
                    vals = {
                        "name": location['id'],
                        "error": e,
                        "import_json" : location,
                        "field_type": "location",                           
                        "datetime": datetime.now(),
                        "base_config_id": self.id,
                    }
                    self.env['sh.import.failed'].create(vals)
            if count:
                vals = {
                    "name": self.name,
                    "state": "success",
                    "field_type": "location",
                    "error": "Location Imported Successfully",
                    "datetime": datetime.now(),
                    "base_config_id": self.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)
        else:
            vals = {
                "name": self.name,
                "state": "error",
                "field_type": "location",
                "error": response.text,
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)