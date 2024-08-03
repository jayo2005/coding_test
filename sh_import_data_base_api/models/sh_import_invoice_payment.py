# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"
    

    import_invoice=fields.Boolean("Import Invoice-Payment")
    records_per_page_invoice = fields.Integer("No of records per page")
    current_import_page_invoice = fields.Integer("Current Page",default=0)    


    def import_invoice_payment_cron(self):   
        ''' ========== Import Sale_orders ==================  '''
        confid = self.env['sh.import.base'].search([],limit=1)
        if confid.import_invoice:
            confid.current_import_page_invoice += 1
            url='''%s/api/public/account.invoice?query={number,origin,payment_ids,payment_move_line_ids{payment_id,invoice_id},state,date,date_due,date_invoice,
            amount_tax,amount_total,amount_total_signed,amount_untaxed,residual,type,id,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},
            zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,
            phone,mobile,id,company_type,customer,child_ids}},journal_id{id,type,code},invoice_line_ids{*,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},
            country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,
            is_company,phone,mobile,id,company_type,customer,child_ids}},invoice_line_tax_ids{name,amount,type_tax_use},product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},
            supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,
            phone,mobile,id,company_type}}}}}}&page_size=%s&page=%s&order="id asc"&filter=[["origin","=",null]]''' %(confid.base_url,confid.records_per_page_invoice,confid.current_import_page_invoice)
            # print(f"==>> url: {url}")  
            response = requests.get(url)
            # print(f"==>> response: {response}") 
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('count') and confid.records_per_page_invoice != response_json['count']:
                    confid.import_invoice = False
                    confid.current_import_page_invoice = 0
                count = 0
                failed = 0

                already_invoice=False
                invoice_ids=[]
                invoice_dict={}
                payment_list=[]
                credit_note=[]
                for data in response_json.get('result'):
                    try:
                        invoice_dict[str(data.get('id'))]=data.get('state').get('sh_api_current_state')
                        invoice_list,payment_list=confid.process_invoice_data([data])
                        for invoice in invoice_list:
                            invoice_id=self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])                                        
                            if not invoice_id:
                                if invoice[2].get('state'):
                                    invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                    del invoice[2]['state']
                                created_invoice=self.env['account.move'].create(invoice[2])
                                count+=1
                            else:     
                                if invoice[2].get('state'):
                                    invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                    del invoice[2]['state']    
                                remove_lines=[]
                                if invoice[2] and invoice[2].get('invoice_line_ids'):
                                    for line in invoice[2].get('invoice_line_ids'):
                                        if line[2] and line[2].get('remote_account_move_line_id'):
                                            find_line = self.env['account.move.line'].search([('remote_account_move_line_id','=',line[2].get('remote_account_move_line_id'))],limit=1)
                                            if find_line:
                                                remove_lines.append(line)
                                if remove_lines:
                                    for r_line in remove_lines:
                                        invoice[2].get('invoice_line_ids').remove(r_line)          
                                invoice_id.write(invoice[2])
                                count+=1
                                created_invoice=invoice_id
                            if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                created_invoice.action_post()
                            elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                created_invoice.button_cancel()
                            if created_invoice.move_type=='out_refund':
                                credit_note.append(created_invoice)
                            elif created_invoice.move_type=='out_invoice':
                                invoice_ids.append(created_invoice) 
                        for payment in payment_list:
                            domain=[('remote_account_payment_id','=',payment.get('remote_account_payment_id'))]
                            already_payment = self.env['account.payment'].search(domain,limit=1)
                            if 'invoice_ids' in payment:
                                connected_invoice_ids=payment.get('invoice_ids')
                                
                                del payment['invoice_ids']
                            state='draft'
                            if already_payment:
                                created_payment=already_payment
                                created_payment.write(payment)
                                if created_payment.state!='posted':
                                    created_payment.action_post()
                            else:
                                if payment.get('state') in ['posted','sent','reconciled']:
                                    state='posted'
                                    payment['state']='draft'
                                elif payment.get('state')=='cancelled':
                                    state='cancel'
                                    payment['state']='draft'
                                created_payment = self.env['account.payment'].create(payment)
                                created_payment.action_post()
                            if created_payment and connected_invoice_ids:   
                                for inv in connected_invoice_ids:
                                    invoice=self.env['account.move'].search([('remote_account_move_id','=',inv)])
                                    if invoice and invoice.state=='posted':  
                                        lines = (created_payment.line_ids + invoice.line_ids).filtered(
                                            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
                                        lines.reconcile()
                            if created_payment.state!=state:
                                self.env.cr.execute(''' UPDATE account_move set state=%s where id = %s ''', [state,created_payment.move_id.id])      

                        # ============================================================
                        # CONNECT INVOICE AND CREDIT NOTE ( INVOICE AND CREDIT NOTE 
                        # JOURNAL ENTRY RECONCILE )
                        # ============================================================ 
                        for note in credit_note:
                            if note and data.get('invoice_ids'):   
                                for inv in data.get('invoice_ids'):
                                    invoice=self.env['account.move'].search([('remote_account_move_id','=',inv.get('id'))])
                                    if invoice and invoice.state=='posted':  
                                        lines = (note.line_ids + invoice.line_ids).filtered(
                                            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
                                        lines.reconcile()
                

                    except Exception as e:
                        failed += 1
                        vals = {
                            "name": data['id'],
                            "error": e,
                            "import_json" : data,
                            "field_type": "invoice",                           
                            "datetime": datetime.now(),
                            "base_config_id": confid.id,
                        }
                        self.env['sh.import.failed'].create(vals)
                if count > 0:              
                    vals = {
                        "name": confid.name,
                        "state": "success",
                        "field_type": "invoice",
                        "error": "%s Invoice Imported Successfully" %(count-failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)
                if failed > 0:
                    vals = {
                        "name": confid.name,
                        "state": "error",
                        "field_type": "invoice",
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
                    "field_type": "invoice",
                    "error": response.text,
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)