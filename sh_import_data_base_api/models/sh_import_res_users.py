
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"
    
    def process_user_data(self,data):
        ''' ============== Prepare SalesPerson ====================== '''
        if 'login' in data and data['login']:
            user_vals = {
                'remote_user_id':data.get('id'),
                'active' : data.get('active'),  
                'active_partner':data.get('active_partner'),
                'barcode':data.get('barcode'),
                'city' : data.get('city'),  
                'color':data.get('color'),
                'comment':data.get('comment'),
                'contact_address':data.get('contact_address'),
                # 'lang':data.get('lang').get('sh_api_current_state'),
                'login' : data.get('login'),  
                'mobile':data.get('mobile'),
                'name':data.get('name'),
                'new_password':data.get('new_password'),
                'credit_limit' : data.get('credit_limit'),  
                'debit':data.get('debit'),
                'debit_limit':data.get('debit_limit'),
                'display_name':data.get('display_name'),
                'email':data.get('email'),
                'email_formatted':data.get('email_formatted'),
                'password' : data.get('password'),  
                'phone':data.get('phone'),
                'state':data.get('state'),            
                'street':data.get('street'),
                'street2':data.get('street2'),
                # 'type':data.get('type'),
                'vat':data.get('vat'),
                'tz':data.get('tz').get('sh_api_current_state'),
                'tz_offset':data.get('tz_offset'),
            }     
            if data['state_id']:
                domain = [('name','=',data['state_id']['name'])]
                find_state = self.env['res.country.state'].search(domain)
                if find_state:
                    user_vals['state_id'] = find_state.id
            if data['country_id']:
                country_domain = [('name', '=', data['country_id']['name'])]
                find_country = self.env['res.country'].search(country_domain)
                if find_country:
                    user_vals['country_id'] = find_country.id 
                    
            if data.get('partner_id'):
                domain = [('remote_partner_id', '=', data['partner_id']['id'])]
                find_customer = self.env['res.partner'].search(domain)
                if find_customer:
                    user_vals['partner_id'] = find_customer.id
                else:
                    contact_vals=self.process_contact_data(data['partner_id'])
                    partner_id=self.env['res.partner'].create(contact_vals)
                    if partner_id:
                        user_vals['partner_id']=partner_id.id 
            return user_vals
        return False
    