# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class ImportBase(models.Model):
    _name = "sh.import.base"
    _description = "Import Base"

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Name',required=True,copy=False)
    base_url = fields.Char("Base Url")
    import_product = fields.Boolean("Import Products")
    
    records_per_page = fields.Integer("No of records per page")
    
    state = fields.Selection([('draft','Draft'),('success','Success')],default="draft",string="State")
    current_import_page = fields.Integer("Current Page",default=0)
    
    log_historys = fields.One2many(
        'sh.import.base.log', 'base_config_id', string="Log History")
    failed_history = fields.One2many(
        'sh.import.failed', 'base_config_id', string="Failed History")

    def connect_database(self):        
        response = requests.get('%s/api/public/product.category?query={id,name, parent_id{name}}' %(self.base_url))
        if response.status_code == 200:
            self.state = 'success'
            vals = {
                "name": self.name,
                "state": "success",
                "field_type": "auth",
                "error": "Connection Successful",
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)
            self.import_product_category()
            self.import_unit_of_measure()
            self.import_locations()
            self.import_warehouses()
        else:
            vals = {
                "name": self.name,
                "state": "error",
                "field_type": "auth",
                "error": response.text,
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)

    def import_product_category(self):
        response = requests.get('%s/api/public/product.category?query={id,name, parent_id{name}}' %(self.base_url))
        if response.status_code == 200:
            response_json = response.json()
            total_count = response_json['count']
            count = 0
            for categ in response_json['result']:
                domain = [('name', '=', categ['name'])]
                find_category = self.env['product.category'].search(domain)
                if find_category:
                    count += 1
                    find_category.write({
                        'remote_product_category_id' : categ['id'],
                    })
                else:
                    categ_vals = {
                        'name' : categ['name'],
                        'remote_product_category_id' : categ['id'],
                    }
                    if categ['parent_id']['name'] != '':
                        domain = [('name', '=', categ['parent_id']['name'])]
                        find_parent_id = self.env['product.category'].search(domain)
                        if find_parent_id:
                            categ_vals['parent_id'] = find_parent_id.id
                    self.env['product.category'].create(categ_vals)
                    count += 1
            if count == total_count:
                vals = {
                    "name": self.name,
                    "state": "success",
                    "field_type": "category",
                    "error": "All Category Imported Successfully",
                    "datetime": datetime.now(),
                    "base_config_id": self.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)
        else:
            vals = {
                "name": self.name,
                "state": "error",
                "field_type": "category",
                "error": response.text,
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)

    def import_unit_of_measure(self):
        response = requests.get('%s/api/public/uom.uom?query={id,name,uom_type,factor,rounding,category_id{*}}' %(self.base_url))
        if response.status_code == 200:
            response_json = response.json()
            total_count = response_json['count']
            count = 0
            for uom in response_json['result']:
                domain = []
                if  uom['name'] == 'Day(s)':
                    domain = [('name','=','Days')]
                elif  uom['name'] == 'Dozen(s)':
                    domain = [('name','=','Dozens')]
                elif  uom['name'] == 'Hour(s)':
                    domain = [('name','=','Hours')]
                elif  uom['name'] == 'Liter(s)':
                    domain = [('name','=','L')]
                elif  uom['name'] == 'Unit(s)':
                    domain = [('name','=','Units')]
                elif  uom['name'] == 'cm':
                    domain = [('name','=','cm')]
                elif  uom['name'] == 'fl oz':
                    domain = [('name','=','fl oz (US)')]
                elif  uom['name'] == 'foot(ft)':
                    domain = [('name','=','ft')]
                elif  uom['name'] == 'g':
                    domain = [('name','=','g')]
                elif  uom['name'] == 'gal(s)':
                    domain = [('name','=','gal (US)')]
                elif  uom['name'] == 'inch(es)':
                    domain = [('name','=','in')]
                elif  uom['name'] == 'kg':
                    domain = [('name','=','kg')]
                elif  uom['name'] == 'km':
                    domain = [('name','=','km')]
                elif  uom['name'] == 'lb(s)':
                    domain = [('name','=','lb')]
                elif  uom['name'] == 'm':
                    domain = [('name','=','m')]
                elif  uom['name'] == 'mile(s)':
                    domain = [('name','=','mi')]
                elif  uom['name'] == 'oz(s)':
                    domain = [('name','=','oz')]
                elif  uom['name'] == 'qt':
                    domain = [('name','=','qt (US)')]
                elif  uom['name'] == 't':
                    domain = [('name','=','t')]
                else:
                    domain = [('name', '=', uom['name'])]

                find_uom = False
                if domain:
                    find_uom = self.env['uom.uom'].search(domain)
                if not find_uom:
                    uom_vals = {
                        'name' : uom['name'],
                        'rounding':uom['rounding'],
                        'uom_type':uom['uom_type']['sh_api_current_state'],                        
                        'remote_uom_id':uom['id']
                    }
                    category = self.process_category(uom['category_id'])
                    if category:
                        uom_vals['category_id'] = category.id
                    uom_type = uom['uom_type']['sh_api_current_state']
                    if uom_type == 'reference':
                        uom_vals.update({'ratio':1})
                    elif uom_type == 'bigger':
                        uom_vals.update({'ratio':1/ uom['factor']})
                    elif uom_type == 'smaller':
                        uom_vals.update({'ratio':uom['factor']})
                    self.env['uom.uom'].sudo().create(uom_vals)
                else:
                    find_uom.sudo().write({'remote_uom_id':uom['id']})
                count += 1
            if count == total_count:
                vals = {
                    "name": self.name,
                    "state": "success",
                    "field_type": "uom",
                    "error": "Unit of Measure Imported Successfully",
                    "datetime": datetime.now(),
                    "base_config_id": self.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)
        else:
            vals = {
                "name": self.name,
                "state": "error",
                "field_type": "uom",
                "error": response.text,
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            }
            self.env['sh.import.base.log'].create(vals)

    def process_category(self,category):
        domain = ['|',('name', '=', category['name']),('remote_uom_category_id', '=', category['id'])]
        find_category = self.env['uom.category'].search(domain,limit=1)
        if find_category:
            find_category.write({
                'remote_uom_category_id' : category['id']
            })
            return find_category
        else:
            categ_vals = {
                'name' : category['name'],
                'measure_type' : category['measure_type']['sh_api_current_state'],
                'remote_uom_category_id' : category['id']
            }
            created_category = self.env['uom.category'].create(categ_vals)
            return created_category                    


    def import_product_cron(self):   
        confid = self.env['sh.import.base'].search([],limit=1)
        if confid.import_product:
            confid.current_import_page += 1
            response = requests.get('%s/api/public/product.template?query={*, taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use}, seller_ids{*,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}&page_size=%s&page=%s' %(confid.base_url,confid.records_per_page,confid.current_import_page))
            if response.status_code == 200:
                response_json = response.json()
                if confid.records_per_page != response_json['count']:
                    confid.import_product = False
                    confid.current_import_page = 0
                count = 0
                failed = 0
                for data in response_json['result']:
                    product_vals = confid.process_product_data(data)
                    domain = [('remote_product_template_id', '=', data['id'])]
                    already_product = self.env['product.template'].search(domain,limit=1)
                    try:
                        if already_product:
                            count += 1
                            already_product.write(product_vals)
                            if data.get('seller_ids'):
                                self.process_seller_ids(data['seller_ids'],already_product)
                        else:
                            count += 1
                            created_product = self.env['product.template'].create(product_vals)
                            if data.get('seller_ids'):
                                self.process_seller_ids(data['seller_ids'],created_product)
                    except Exception as e:
                        failed += 1
                        vals = {
                            "name": data['id'],
                            "error": e,
                            "import_json" : data,
                            "field_type": "product",                           
                            "datetime": datetime.now(),
                            "base_config_id": confid.id,
                        }
                        self.env['sh.import.failed'].create(vals)  
                if count > 0:              
                    vals = {
                        "name": confid.name,
                        "state": "success",
                        "field_type": "product",
                        "error": "%s Product Imported Successfully" %(count - failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)
                if failed > 0:
                    vals = {
                        "name": confid.name,
                        "state": "error",
                        "field_type": "product",
                        "error": "%s Failed To Import" %(failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)

            else:
                vals = {
                    "name": confid.name,
                    "state": "error",
                    "field_type": "product",
                    "error": response.text,
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)

    def process_product_data(self,data):
        product_vals = {
            'name' : data.get('name',''),
            'description' : data.get('description',''),
            'description_purchase' : data.get('description_purchase',''),
            'description_sale' : data.get('description_sale',''),
            'list_price' : data.get('list_price',''),
            'standard_price' : data.get('standard_price',''),
            'volume' : data.get('volume',0.0),
            'weight' : data.get('weight',0.0),
            'sale_ok' : data.get('sale_ok'),
            'purchase_ok' : data.get('purchase_ok'),
            'color' : data.get('color'),
            'barcode' : data.get('barcode',''),
            'default_code' : data.get('default_code'),
            'detailed_type' : 'product',
            'invoice_policy' : data['invoice_policy']['sh_api_current_state'],
            'expense_policy' : data['expense_policy']['sh_api_current_state'],
            'active' : data['active'],
            'remote_product_template_id' : data['id'],
            'pricelist_exception' : data.get('pricelist_exception',False),
            'excluded_from_disocunt' : data.get('excluded_from_disocunt',False),
            'sqmter_per_box' : data.get('sqyard_per_box',0.0),
            'sqmeter_price' : data.get('sqmeter_price',0.0),
            'sq_cost' : data.get('sq_cost',0.0),
            'sqyards_ina_box' : data.get('sqyards_ina_box',0.0),
            'sqyard_price' : data.get('sqyard_price',0.0),
            'length' : data.get('length',''),
            'width' : data.get('width',''),
            'height' : data.get('height',''),
        }
        domain = [('remote_product_category_id', '=', data['categ_id'])]
        find_category = self.env['product.category'].search(domain)
        if find_category:
            product_vals['categ_id'] = find_category.id
        if data['taxes_id']:
            tax_list = self.process_tax(data['taxes_id'])
            if tax_list:
                product_vals['taxes_id'] = tax_list
        if data['supplier_taxes_id']:
            supplier_tax_list = self.process_tax(data['supplier_taxes_id'])
            if supplier_tax_list:
                product_vals['supplier_taxes_id'] = supplier_tax_list
        return product_vals

    
    def process_tax(self,taxes):
        tax_list = []
        for value in taxes:
            domain = [('amount', '=', value['amount']),('type_tax_use', '=', value['type_tax_use']['sh_api_current_state'])]
            find_tax = self.env['account.tax'].search(domain,limit=1)
            if find_tax:
                tax_list.append(find_tax.id)
            else:
                tax_vals = {
                    'name' : value['name'],
                    'amount' : value['amount'],
                    'type_tax_use' : value['type_tax_use']['sh_api_current_state'],
                    'amount_type' : 'percent',
                }
                create_tax = self.env['account.tax'].create(tax_vals)
                tax_list.append(create_tax.id)
        return tax_list

    def process_seller_ids(self,seller_ids,product_tmpl_id):
        for seller in seller_ids:
            vendor = self.get_proper_vendor(seller['name'])
            seller_vals = {
                'partner_id' : vendor.id,
                'price' :  seller['price'],
                'product_code' : seller['product_code'],
                'product_name' : seller['product_name'],
                'min_qty' : seller['min_qty'],
                'product_tmpl_id' : product_tmpl_id.id
            }
            if seller.get('date_start') != '':
                seller_vals['date_start'] = seller.get('date_start')
            if seller.get('date_end') != '':
                seller_vals['date_end'] = seller.get('date_end')
            domain = [('remote_uom_id', '=', seller['product_uom'])]
            find_uom = self.env['uom.uom'].search(domain)
            if find_uom:
                seller_vals['product_uom'] = find_uom.id
            domain = [('remote_supplierinfo_id', '=', seller['id'])]
            find_supplierinfo = self.env['product.supplierinfo'].search(domain)
            if find_supplierinfo:
                find_supplierinfo.write(seller_vals)
            else:
                self.env['product.supplierinfo'].create(seller_vals)
        return []

    def get_proper_vendor(self,vendor):
        domain = [('remote_partner_id', '=', vendor['id'])]
        find_vendor = self.env['res.partner'].search(domain)
        if find_vendor:
            return find_vendor
        else:
            vendor_vals = {
                'name' : vendor.get('name'),
                'email' : vendor.get('email'),
                'type' : vendor.get('type')['sh_api_current_state'],
                'website' : vendor.get('website'),
                'street' : vendor.get('street'),
                'phone' : vendor.get('phone'),
                'mobile' : vendor.get('mobile'),
                'company_type' : vendor.get('company_type')['sh_api_current_state'],
                'ref' : vendor.get('ref'),
                'is_company' : vendor.get('is_company'),
                'remote_partner_id' : vendor.get('id')
            }
            if vendor['supplier']:
                vendor_vals['supplier_rank'] = 1
            create_vendor = self.env['res.partner'].create(vendor_vals)
            return create_vendor