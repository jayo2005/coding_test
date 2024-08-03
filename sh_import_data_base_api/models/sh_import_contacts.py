# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"

    current_partner_page = fields.Integer("Current Partner Page", default=0)
    import_contacts = fields.Boolean("Import Contacts")

    def import_contacts_cron(self):
        confid = self.env['sh.import.base'].search([], limit=1)
        if confid.import_contacts:
            confid.current_partner_page += 1
            response = requests.get('%s/api/public/res.partner?query={name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id,zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}}&page_size=%s&page=%s' % (confid.base_url, confid.records_per_page, confid.current_partner_page))
            if response.status_code == 200:
                response_json = response.json()
                if confid.records_per_page != response_json['count']:
                    confid.import_contacts = False
                    confid.current_partner_page = 0
                count = 0
                failed = 0
                for data in response_json['result']:
                    contact_vals = confid.process_contact_data(data)
                    domain = [('remote_partner_id', '=', data['id'])]
                    find_contact = self.env['res.partner'].search(domain)
                    try:
                        if find_contact:
                            count += 1
                            find_contact.write(contact_vals)
                        else:
                            count += 1
                            self.env['res.partner'].create(contact_vals)
                    except Exception as e:
                        failed += 1
                        vals = {
                            "name": data['id'],
                            "error": e,
                            "import_json": data,
                            "field_type": "customer",
                            "datetime": datetime.now(),
                            "base_config_id": confid.id,
                        }
                        self.env['sh.import.failed'].create(vals)
                if count > 0:
                    vals = {
                        "name": confid.name,
                        "state": "success",
                        "field_type": "customer",
                        "error": "%s Contacts Imported Successfully" % (count - failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)
                if failed > 0:
                    vals = {
                        "name": confid.name,
                        "state": "error",
                        "field_type": "customer",
                        "error": "%s Failed To Import" % (failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)
            else:
                vals = {
                    "name": confid.name,
                    "state": "error",
                    "field_type": "customer",
                    "error": response.text,
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)

    def process_contact_data(self, contact):
        contact_vals = {
            'name': contact.get('name'),
            'email': contact.get('email'),
            'type': contact.get('type')['sh_api_current_state'],
            'website': contact.get('website'),
            'street': contact.get('street'),
            'phone': contact.get('phone'),
            'mobile': contact.get('mobile'),
            'company_type': contact.get('company_type')['sh_api_current_state'],
            'ref': contact.get('ref'),
            'is_company': contact.get('is_company'),
            'remote_partner_id': contact.get('id'),
            'street2': contact.get('street2'),
            'city': contact.get('city'),
            'zip': contact.get('zip'),
            'vat': contact.get('vat')
        }

        if contact.get('state_id'):
            if isinstance(contact['state_id'], dict) and 'name' in contact['state_id']:
                state_domain = [('name', '=', contact['state_id']['name'])]
            else:
                state_domain = [('id', '=', contact['state_id'])]
            find_state = self.env['res.country.state'].search(state_domain)
            if find_state:
                contact_vals['state_id'] = find_state.id

        if contact.get('country_id'):
            if isinstance(contact['country_id'], dict) and 'name' in contact['country_id']:
                country_domain = [('name', '=', contact['country_id']['name'])]
            else:
                country_domain = [('id', '=', contact['country_id'])]
            find_country = self.env['res.country'].search(country_domain)
            if find_country:
                contact_vals['country_id'] = find_country.id

        if contact.get('supplier'):
            contact_vals['supplier_rank'] = 1

        if contact.get('customer'):
            contact_vals['customer_rank'] = 1

        if contact.get('child_ids'):
            child_list = []
            for child in contact['child_ids']:
                child_vals = self.process_contact_data(child)
                domain = [('remote_partner_id', '=', child['id'])]
                find_child = self.env['res.partner'].search(domain)
                if not find_child:
                    child_list.append((0, 0, child_vals))
            contact_vals['child_ids'] = child_list

        return contact_vals

