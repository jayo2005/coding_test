# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models
import requests

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    remote_product_template_id = fields.Char("Remote Product Template ID")
    pricelist_exception = fields.Boolean("Pricelist Exception")
    excluded_from_disocunt = fields.Boolean(string="Excluded from Discount")
    
    def sh_update_sqmter_per_box(self):
        confid = self.env['sh.import.base'].search([],limit=1)
        for product in self.browse(self.env.context['active_ids']):
            if product.remote_product_template_id:
                response = requests.get('%s/api/public/product.template/%s?query={id,sqyards_per_box}' %(confid.base_url,product.remote_product_template_id))
                if response.status_code == 200:
                    response_json = response.json()
                    for data in response_json['result']:
                        domain = [('remote_product_template_id', '=', data['id'])]
                        find_product = self.env['product.template'].search(domain,limit=1)
                        try:
                            if find_product:
                                find_product.write({
                                    'sqmter_per_box':data['sqyards_per_box']
                                })                                
                        except Exception as e:
                            print(e)

    def convert_product_storable(self):
        for product in self.browse(self.env.context['active_ids']):
            product.write({
                'detailed_type' : 'product'
            })


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    remote_supplierinfo_id = fields.Char("Remote Supplierinfo Id")