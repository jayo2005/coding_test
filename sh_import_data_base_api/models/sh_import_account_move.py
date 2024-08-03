# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models
import requests
import json
from datetime import datetime

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"
    
    def process_account_move_data(self,data):
        ''' ================= Import Account Moves =============  '''
        invoice_line_list=[]
        for line in data:
            
            line_vals={}
            if line.get('display_type') and line.get('display_type').get('sh_api_current_state') and line.get('display_type').get('sh_api_current_state')=='line_section' or line.get('display_type').get('sh_api_current_state')=='line_note':
                line_vals={
                    'remote_account_move_line_id':line.get('id'),
                    'name':line.get('name'),
                    'display_type':line.get('display_type').get('sh_api_current_state'),
                }
            else:
                line_vals={
                    'remote_account_move_line_id':line.get('id'),
                    'discount':line.get('discount'),
                    'move_type':line.get('invoice_type').get('sh_api_current_state'),
                    'price_subtotal':line.get('price_subtotal'),
                    'price_total':line.get('price_total'),
                    'price_unit':line.get('price_unit'),
                    'quantity':line.get('quantity'),
                }
                
                # ======== Get partner if already created or create =====
                
                if line.get('partner_id'):
                    domain = [('remote_partner_id', '=', line['partner_id']['id'])]
                    find_customer = self.env['res.partner'].search(domain)
                    if find_customer:
                        line_vals['partner_id'] = find_customer.id
                    else:
                        contact_vals=self.process_contact_data(line['partner_id'])
                        partner_id=self.env['res.partner'].create(contact_vals)
                        if partner_id:
                            line_vals['partner_id']=partner_id.id
                            
                # ======== Get Product if already created or create =====             
                            
                if line.get('product_id'):
                    domain = [('remote_product_template_id', '=', line['product_id']['product_tmpl_id']['id'])]
                    find_product = self.env['product.template'].search(domain,limit=1)
                    if find_product:
                        find_product_var = self.env['product.product'].search([('product_tmpl_id','=',find_product.id)],limit=1)
                        if find_product_var:
                            line_vals['product_id'] = find_product_var.id
                            line_vals['name'] = find_product_var.display_name
                        else:
                            product_vals=self.process_product_data(line['product_id']['product_tmpl_id'])
                            product_id=self.env['product.template'].create(product_vals)
                            if product_id:
                                find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
                                if find_product_var:
                                    line_vals['product_id']=find_product_var.id
                                    line_vals['name'] = find_product_var.display_name
                                else:
                                    check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
                                    line_vals['product_id'] = check_archived_product.id
                    else:
                        product_vals=self.process_product_data(line['product_id']['product_tmpl_id'])
                        product_id=self.env['product.template'].create(product_vals)
                        if product_id:
                            find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
                            if find_product_var:
                                line_vals['product_id'] = find_product_var.id
                                line_vals['name'] = find_product_var.display_name   
                            else:
                                check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
                                line_vals['product_id'] = check_archived_product.id    
            if line_vals:      
                move_id=self.env['account.move.line'].search([('remote_account_move_line_id','=',line.get('id'))])
                if move_id:
                    if move_id.reconciled:
                        move_id.remove_move_reconcile()
                    if 'partner_id' in line_vals:
                        del line_vals['partner_id']
                    move_id.write(line_vals)  
                else:               
                    invoice_line_list.append((0,0,line_vals))                   
        return invoice_line_list               
                        
    def process_invoice_data(self,data):
        ''' ================= Import Invoices =============  '''
        invoice_list=[]
        payment_list = []
        for invoice in data:
            invoice_vals={
                'name':invoice.get('number'),
                # 'number':invoice.get('number'),
                'amount_tax':invoice.get('amount_tax'),
                'amount_total':invoice.get('amount_total'),
                'amount_total_signed':invoice.get('amount_total_signed'),
                'amount_untaxed':invoice.get('amount_untaxed'),
                'amount_residual':invoice.get('residual'),
                'move_type':invoice.get('type').get('sh_api_current_state'),
                'remote_account_move_id':invoice.get('id'),
                'invoice_origin':invoice.get('origin'),
            }
            
            if invoice.get('date'):
                date_time=datetime.strptime(invoice.get('date'),'%Y-%m-%d')
                invoice_vals['date']=date_time
                
            if invoice.get('date_due'):
                date_time=datetime.strptime(invoice.get('date_due'),'%Y-%m-%d')
                invoice_vals['invoice_date_due']=date_time
                
            if invoice.get('date_invoice'):
                date_time=datetime.strptime(invoice.get('date_invoice'),'%Y-%m-%d')
                invoice_vals['invoice_date']=date_time
            
            # ======== Get partner if already created or create =====
            if invoice.get('partner_id'):
                domain = [('remote_partner_id', '=', invoice['partner_id']['id'])]
                find_customer = self.env['res.partner'].search(domain)
                if find_customer:
                    invoice_vals['partner_id'] = find_customer.id
                else:
                    contact_vals=self.process_contact_data(invoice['partner_id'])
                    partner_id=self.env['res.partner'].create(contact_vals)
                    if partner_id:
                        invoice_vals['partner_id']=partner_id.id
            
            # ============== Manage Journal ==========
            if invoice.get('journal_id') and invoice.get('journal_id').get('id') and invoice.get('journal_id').get('id')!=0:
                domain=['|',('remote_account_journal_id','=',invoice.get('journal_id').get('id')),('code', '=', invoice['journal_id']['code']),('type', '=', invoice['journal_id']['type']['sh_api_current_state'])]
                find_journal=self.env['account.journal'].search(domain,limit=1)
                if find_journal:
                    invoice_vals['journal_id']=find_journal.id
                else:
                    journal_vals=self.process_account_journal_data(invoice.get('journal_id'))
                    if journal_vals:
                        created_journal = self.env['account.journal'].create(journal_vals)
                        if created_journal:
                            invoice_vals['journal_id']=created_journal.id

            # ======== Prepare Invoice lines ==========
                                
            if invoice.get('invoice_line_ids'):
                invoice_line_list = self.process_account_move_data(invoice.get('invoice_line_ids'))
                if invoice_line_list:
                    invoice_vals['invoice_line_ids']= invoice_line_list
            
            # if invoice.get('payment_ids'):
            #     payment_list=self.import_account_payment(invoice.get('payment_ids')) 
            if invoice.get('payment_move_line_ids'):
                payment_list=[]
                for line in invoice.get('payment_move_line_ids'):
                    if line.get('payment_id'):
                        payment=self.import_account_payment(line.get('payment_id')) 
                        payment_list.append(payment)
                    elif line.get('invoice_id'):
                        credit_note=self.import_credit_note(line.get('invoice_id')) 
                        invoice_list.append((0,0,credit_note))   
            invoice_list.append((0,0,invoice_vals))    
        return invoice_list,payment_list
    
    def import_account_payment(self,payment_id):
        response = requests.get('''%s/api/public/account.payment?query={*,cashier{id,active,active_partner,alias_contact,allow_create_order_line,allow_delete_order,allow_discount,allow_edit_price,allow_manual_customer_selecting,allow_payments,allow_refund,allow_refund,barcode,city,color,comment,contact_address,country_id{name},credit,lang,login,mobile,name,new_password,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name },zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},credit_limit,customer,customer_credit,customer_credit_limit,debit,debit_limit,delivery_instructions,delivery_terms,display_name,email,email_formatted, password,phone,state,state_id{name },street,street2,supplier,type,vat,tz,tz_offset}
            ,destination_journal_id{*,account_control_ids{*,tag_ids{*},tax_ids{*}, user_type_id{*}},outbound_payment_method_ids{*},type_control_ids{*},bank_account_id{*,bank_id{*,state{id,name},country{id,name}}},
            bank_id{*,state{id,name}}, default_credit_account_id{*,tag_ids{*},tax_ids{*},user_type_id{*}}, default_debit_account_id{*,tag_ids{*},tax_ids{*},user_type_id{*}}, loss_account_id{*,tag_ids{*},tax_ids{*},user_type_id{*}}, profit_account_id{*,tag_ids{*},tax_ids{*},user_type_id{* } } }, 
            journal_id{*,account_control_ids{*,tag_ids{*},tax_ids{*},user_type_id{*}},outbound_payment_method_ids{*},type_control_ids{*},bank_account_id{*,bank_id{*,state{id,name},country{id,name}}},bank_id{*,state{id,name},country{id,name}}, default_credit_account_id { *, tag_ids{* }, tax_ids{* }, user_type_id{* } }, default_debit_account_id { *, tag_ids{* }, tax_ids{* }, user_type_id{* } }, loss_account_id { *, tag_ids{* }, tax_ids{* }, user_type_id{* } }, profit_account_id { *, tag_ids{* }, tax_ids{* }, user_type_id{* } } },
            partner_id { name,vat,title,ref,type,website,street,street2,city,state_id{name },country_id{name },zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name },country_id{name },zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
            payment_method_id{*},writeoff_account_id{id,name},move_line_ids{*},reconciled_invoice_ids{*,-amount_by_group}}
            &filter=[["id","=",%s]]''' %(self.base_url,payment_id))
        if response.status_code == 200:
            response_json = response.json()
            for data in response_json.get('result'):
                payment_data=self.process_account_payment_data(data)
            return payment_data
    
    def import_credit_note(self,note_id):
        response = requests.get('''%s/api/public/account.invoice?query={number,origin,payment_ids,state,date,date_due,date_invoice,amount_tax,
            amount_total,amount_total_signed,amount_untaxed,residual,type,id,partner_id{name,vat,title,
            ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,
            phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,
            city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
            journal_id{id,type,code},invoice_line_ids{*,partner_id{name,vat,title,ref,type,website,supplier,street,
            street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,
            child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,
            is_company,phone,mobile,id,company_type,customer,child_ids}},invoice_line_tax_ids{name,amount,type_tax_use},product_id
            {id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},
            seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,
            street,email,is_company,phone,mobile,id,company_type}}}}}}
            &filter=[["id","=",%s]]''' %(self.base_url,note_id))
        if response.status_code == 200:
            response_json = response.json()
            for data in response_json.get('result'):
                credit_note=self.process_credit_invoice_data(data)
            return credit_note     
    
    
    def process_credit_invoice_data(self,invoice):
        ''' ================= Import Invoices =============  '''
        invoice_vals={
            'name':invoice.get('number'),
            # 'number':invoice.get('number'),
            'amount_tax':invoice.get('amount_tax'),
            'amount_total':invoice.get('amount_total'),
            'amount_total_signed':invoice.get('amount_total_signed'),
            'amount_untaxed':invoice.get('amount_untaxed'),
            'amount_residual':invoice.get('residual'),
            'move_type':invoice.get('type').get('sh_api_current_state'),
            'remote_account_move_id':invoice.get('id'),
            'invoice_origin':invoice.get('origin'),
            'state':invoice.get('state').get('sh_api_current_state'),
        }
        # if invoice.get('state') and invoice.get('state').get('sh_api_current_state'):
        #     if invoice.get('state').get('sh_api_current_state')=='draft':
        #         invoice_vals['state']='draft'
        #     elif invoice.get('state').get('sh_api_current_state') in ['open','in_payment','paid']:
        #         invoice_vals['state']='posted'
        #     elif invoice.get('state').get('sh_api_current_state') =='cancel':
        #         invoice_vals['state']='cancel'
        # print("\n\==========invoice_vals['state']=",invoice_vals['state'])         
        if invoice.get('date'):
            date_time=datetime.strptime(invoice.get('date'),'%Y-%m-%d')
            invoice_vals['date']=date_time
            
        if invoice.get('date_due'):
            date_time=datetime.strptime(invoice.get('date_due'),'%Y-%m-%d')
            invoice_vals['invoice_date_due']=date_time
            
        if invoice.get('date_invoice'):
            date_time=datetime.strptime(invoice.get('date_invoice'),'%Y-%m-%d')
            invoice_vals['invoice_date']=date_time
        
        # ======== Get partner if already created or create =====
        if invoice.get('partner_id'):
            domain = [('remote_partner_id', '=', invoice['partner_id']['id'])]
            find_customer = self.env['res.partner'].search(domain)
            if find_customer:
                invoice_vals['partner_id'] = find_customer.id
            else:
                contact_vals=self.process_contact_data(invoice['partner_id'])
                partner_id=self.env['res.partner'].create(contact_vals)
                if partner_id:
                    invoice_vals['partner_id']=partner_id.id
        
        # ============== Manage Journal ==========
        if invoice.get('journal_id') and invoice.get('journal_id').get('id') and invoice.get('journal_id').get('id')!=0:
            domain=['|',('remote_account_journal_id','=',invoice.get('journal_id').get('id')),('code', '=', invoice['journal_id']['code']),('type', '=', invoice['journal_id']['type']['sh_api_current_state'])]
            find_journal=self.env['account.journal'].search(domain,limit=1)
            if find_journal:
                invoice_vals['journal_id']=find_journal.id
            else:
                journal_vals=self.process_account_journal_data(invoice.get('journal_id'))
                if journal_vals:
                    created_journal = self.env['account.journal'].create(journal_vals)
                    if created_journal:
                        invoice_vals['journal_id']=created_journal.id

        # ======== Prepare Invoice lines ==========
                            
        if invoice.get('invoice_line_ids'):
            invoice_line_list = self.process_account_move_data(invoice.get('invoice_line_ids'))
            if invoice_line_list:
                invoice_vals['invoice_line_ids']= invoice_line_list
                
        return invoice_vals
    
    
    
    # def process_credit_note_data(self,note):
    #     ''' ================== PREPARE DICT FOR IMPORT CREDIT NOTE  =============   '''   
    #     note_vals={
    #         'remote_account_move_id':note.get('id'),
    #         # 'amount':note.get('amount'),
    #         # 'auto_reverse':note.get('auto_reverse'),
    #         'display_name':note.get('display_name'),
    #         # 'matched_percentage':note.get('matched_percentage'),
    #         'name':note.get('name'),
    #         'narration':note.get('narration'),
    #         'ref':note.get('ref'),
    #     }    
    #     if note.get('date'):
    #         date_time=datetime.strptime(note.get('date'),'%Y-%m-%d')
    #         note_vals['date']=date_time
    #     if note.get('reverse_date'):
    #         date_time=datetime.strptime(note.get('reverse_date'),'%Y-%m-%d')
    #         note_vals['reverse_date']=date_time
    #     # ========== CHECK CONNCTED PARTNER IS EXIST OR NOT  =====================
    #     print("\n\n\======note.get('partner_id')",note.get('partner_id'))
    #     if note.get('partner_id'):
    #         domain = [('remote_partner_id', '=', note['partner_id'])]
    #         find_customer = self.env['res.partner'].search(domain)
    #         if find_customer:
    #             note_vals['partner_id'] = find_customer.id
    #     print("\n\n\======find_customer",find_customer)
    #     # line_ids
    #     if note.get('line_ids'):
    #         invoice_line_list = self.process_account_move_line_data(note.get('line_ids'))
    #         if invoice_line_list:
    #             note_vals['line_ids']= invoice_line_list   
    #     return note_vals
    
    # def process_account_move_line_data(self,lines):
    #     line_list=[]
    #     for line in lines:
    #         line_vals={
    #             'remote_account_move_line_id':line.get('id'),
    #             'amount_currency':line.get('amount_currency'),
    #             'amount_residual':line.get('amount_residual'),
    #             'amount_residual_currency':line.get('amount_residual_currency'), 
    #             'balance':line.get('balance'),
    #             # 'balance_cash_basis':line.get('balance_cash_basis'),
    #             'blocked':line.get('blocked'),
    #             # 'counterpart':line.get('counterpart'),
    #             'credit':line.get('credit'),
    #             # 'credit_cash_basis':line.get('credit_cash_basis'),
    #             'debit':line.get('debit'),
    #             # 'debit_cash_basis':line.get('debit_cash_basis'), 
    #             'display_name':line.get('display_name'),
    #             # 'internal_note':line.get('internal_note'),
    #             'name':line.get('name'), 
    #             # 'narration':line.get('narration'),
    #             'parent_state':line.get('parent_state'),
    #             'product_id':line.get('product_id'),
    #             'quantity':line.get('quantity'),
    #             'reconciled':line.get('reconciled'),
    #             'tax_base_amount':line.get('tax_base_amount'), 
    #             # 'tax_exigible':line.get('tax_exigible'),
    #             'ref':line.get('ref'),   
    #         }
    #         if line.get('expected_pay_date'):
    #             date_time=datetime.strptime(line.get('expected_pay_date'),'%Y-%m-%d')
    #             line_vals['expected_pay_date']=date_time
                
    #         if line.get('next_action_date'):
    #             date_time=datetime.strptime(line.get('next_action_date'),'%Y-%m-%d')
    #             line_vals['next_action_date']=date_time
            
    #         if line.get('date'):
    #             date_time=datetime.strptime(line.get('date'),'%Y-%m-%d')
    #             line_vals['date']=date_time
                
    #         if line.get('date_maturity'):
    #             date_time=datetime.strptime(line.get('date_maturity'),'%Y-%m-%d')
    #             line_vals['date_maturity']=date_time
            
           
                    
    #         # ======== Get Product if already created or create =====             
                            
    #         if line.get('product_id'):
    #             domain = [('remote_product_template_id', '=', line['product_id']['product_tmpl_id']['id'])]
    #             find_product = self.env['product.template'].search(domain,limit=1)
    #             if find_product:
    #                 find_product_var = self.env['product.product'].search([('product_tmpl_id','=',find_product.id)],limit=1)
    #                 if find_product_var:
    #                     line_vals['product_id'] = find_product_var.id
    #                     line_vals['name'] = find_product_var.display_name
    #                 else:
    #                     product_vals=self.process_product_data(line['product_id']['product_tmpl_id'])
    #                     product_id=self.env['product.template'].create(product_vals)
    #                     if product_id:
    #                         find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
    #                         if find_product_var:
    #                             line_vals['product_id']=find_product_var.id
    #                             line_vals['name'] = find_product_var.display_name
    #                         else:
    #                             check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
    #                             line_vals['product_id'] = check_archived_product.id
    #             else:
    #                 product_vals=self.process_product_data(line['product_id']['product_tmpl_id'])
    #                 product_id=self.env['product.template'].create(product_vals)
    #                 if product_id:
    #                     find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
    #                     if find_product_var:
    #                         line_vals['product_id'] = find_product_var.id
    #                         line_vals['name'] = find_product_var.display_name   
    #                     else:
    #                         check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
    #                         line_vals['product_id'] = check_archived_product.id         
                    
    #         line_list.append((0,0,line_vals))    

    #     return line_list
    
    def process_account_account_data(self,data):
        ''' ================== PREPARE DICT FOR IMPORT ACCOUNT  =============   '''                  
        account_vals={
            'remote_account_account_id':data.get('id'),
            'deprecated':data.get('deprecated'),
            'reconcile':data.get('reconcile'),
            'code':data.get('code'),
            'display_name':data.get('display_name'),
            'name':data.get('name'),
            'opening_credit':data.get('opening_credit'),
            'opening_debit':data.get('opening_debit'),
            'internal_group':data.get('internal_group').get('sh_api_current_state'),
            # 'internal_type':data.get('internal_type').get('sh_api_current_state'),
        
        }    
        
        if data.get('last_time_entries_checked'):
            date_time=datetime.strptime(data.get('last_time_entries_checked'),'%Y-%m-%d-%H-%M-%S')
            date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
            account_vals['last_time_entries_checked']=date_time 
          
        # ======== Prepare value for tax which is connected to account =========
        if data.get('tax_ids'):
            tax_list = self.process_tax(data['tax_ids'])
            if tax_list:
                account_vals['tax_ids'] = tax_list  
        
        # ======== Prepare value for Tag which is connected to account ========= 
        if data.get('tag_ids'):
            tag_list =[] 
            for tag in data.get('tag_ids'):
                domain=[('remote_account_tag_id','=',tag.get('id'))]  
                find_tag=self.env['account.account.tag'].search(domain)
                if find_tag:
                    tag_list.append((4,find_tag.id))
                else:
                    tag_vals={
                        'remote_account_tag_id':tag.get('id'),
                        'active':tag.get('active'),
                        'applicability':tag.get('applicability').get('sh_api_current_state'),
                        'color':tag.get('color'),
                        'display_name':tag.get('display_name'),
                        'name':tag.get('name'),
                    }
                    if tag_vals:
                        created_tag = self.env['account.account.tag'].create(tag_vals)
                        if created_tag:
                            tag_list.append((4,created_tag.id)) 
            if tag_list:
                account_vals['tag_ids']=tag_list
                
        # =========== Check if account type is exist or not ===============
        if data.get('user_type_id'):
            if data.get('user_type_id').get('name'):
                if data.get('user_type_id').get('name')=='Fixed Assets':
                    account_vals['account_type']='asset_fixed'
                elif data.get('user_type_id').get('name')=='Current Assets':
                    account_vals['account_type']='asset_current'
                elif data.get('user_type_id').get('name')=='Receivable':
                    account_vals['account_type']='asset_receivable'
                elif data.get('user_type_id').get('name')=='Bank and Cash':
                    account_vals['account_type']='asset_cash'
                elif data.get('user_type_id').get('name')=='Payable':
                    account_vals['account_type']='liability_payable'  
                elif data.get('user_type_id').get('name')=='Non-current Assets':
                    account_vals['account_type']='asset_non_current'
                elif data.get('user_type_id').get('name')=='Prepayments':
                    account_vals['account_type']='asset_prepayments'
                elif data.get('user_type_id').get('name')=='Current Liabilities':
                    account_vals['account_type']='liability_current' 
                elif data.get('user_type_id').get('name')=='Non-current Liabilities':
                    account_vals['account_type']='liability_non_current' 
                elif data.get('user_type_id').get('name')=='Equity':
                    account_vals['account_type']='equity'
                elif data.get('user_type_id').get('name')=='Current Year Earnings':
                    account_vals['account_type']='equity_unaffected'  
                elif data.get('user_type_id').get('name')=='Other Income':
                    account_vals['account_type']='income_other'
                elif data.get('user_type_id').get('name')=='Income':
                    account_vals['account_type']='income'
                elif data.get('user_type_id').get('name')=='Expenses':
                    account_vals['account_type']='expense' 
                elif data.get('user_type_id').get('name')=='Cost of Revenue':
                    account_vals['account_type']='expense_direct_cost'  
                   
        return account_vals     
    
    def process_res_bank_data(self,data):        
        ''' ========== PREPARE VALUE FOR RES BANK WHICH IS CONNECTED WITH PAYMENT =====   '''
        
        res_bank_vals={
            'remote_res_bank_id':data.get('id'),
            'name':data.get('name'),
            'active':data.get('active'),
            'bic':data.get('bic'),
            'city':data.get('city'),
            'display_name':data.get('display_name'),
            'email':data.get('email'),
            'phone':data.get('phone'),
            'street':data.get('street'),
            'street2':data.get('street2'),
            'zip':data.get('zip'),
        }     
        if data['state']:
            domain = [('name','=',data['state']['name'])]
            find_state = self.env['res.country.state'].search(domain)
            if find_state:
                res_bank_vals['state'] = find_state.id
        if data['country']:
            country_domain = [('name', '=', data['country']['name'])]
            find_country = self.env['res.country'].search(country_domain)
            if find_country:
                res_bank_vals['country'] = find_country.id
        
        return res_bank_vals  
    
    def process_res_partner_bank_data(self,data):
        ''' ========== PREPARE VALUE FOR RES PARTNER BANK WHICH IS CONNECTED WITH PAYMENT =====   '''
        
        res_partner_bank_vals={
            'remote_res_partner_bank_id':data.get('id'),
            'acc_holder_name':data.get('acc_holder_name'),
            'acc_number':data.get('acc_number'),
            'acc_type':data.get('acc_type').get('sh_api_current_state'),
            'bank_bic':data.get('bank_bic'),
            'bank_name':data.get('bank_name'),
            'display_name':data.get('display_name'),
            'qr_code_valid':data.get('qr_code_valid'),
            'sanitized_acc_number':data.get('sanitized_acc_number'),
            'sequence':data.get('sequence'),
        }   
        
        # ======== CHECK CONNECTED RES BANK IS EXIST OR NOT ==================
        if data.get('bank_id'):
            domain=['|',('remote_res_bank_id','=',data.get('bank_id').get('id')),('name','=',data.get('bank_id').get('name'))]
            find_res_bank=self.env['res.bank'].search(domain)
            if find_res_bank:
                res_partner_bank_vals['bank_id']=find_res_bank.id
            else:
                res_bank_vals=self.process_res_bank_data(data.get('bank_id'))
                if res_bank_vals:
                    created_res_bank=self.env['res.bank'].create(res_bank_vals)
                    if created_res_bank:
                        res_partner_bank_vals['bank_id']=created_res_bank.id
          
        # ========== CHECK CONNCTED PARTNER IS EXIST OR NOT  =====================
        if data.get('partner_id'):
            domain = [('remote_partner_id', '=', data['partner_id']['id'])]
            find_customer = self.env['res.partner'].search(domain)
            if find_customer:
                res_partner_bank_vals['partner_id'] = find_customer.id
            else:
                contact_vals=self.process_contact_data(data['partner_id'])
                partner_id=self.env['res.partner'].create(contact_vals)
                if partner_id:
                    res_partner_bank_vals['partner_id']=partner_id.id
        
        return res_bank_vals 
    
    def process_account_journal_data(self,data):        
        ''' ===== PREPARE VALUE FOR IMPORT ACCOUNT JOURNAL WHICH ARE CONNECTED WITH PAYMENT ======  '''
        account_journal_vals={
            'remote_account_journal_id':data.get('id'),
            'active':data.get('active'),
            # 'amount_authorized_diff':data.get('amount_authorized_diff'),
            # 'at_least_one_inbound':data.get('at_least_one_inbound'),
            # 'at_least_one_outbound':data.get('at_least_one_outbound'),
            'bank_acc_number':data.get('bank_acc_number'),
            'bank_statements_source':data.get('bank_statements_source').get('sh_api_current_state') if data.get('bank_statements_source') else '',
            # 'belongs_to_company':data.get('belongs_to_company').get('sh_api_current_state') if data.get('belongs_to_company') and data.get('belongs_to_company') else False,
            'code':data.get('code'),
            'color':data.get('color'),
            'display_name':data.get('display_name'),
            # 'group_invoice_lines':data.get('group_invoice_lines'),
            # 'journal_user':data.get('journal_user'),
            'kanban_dashboard':data.get('kanban_dashboard'),
            'kanban_dashboard_graph':data.get('kanban_dashboard_graph'),
            'name':data.get('name'),
            # 'post_at_bank_rec':data.get('post_at_bank_rec'),
            'refund_sequence':data.get('refund_sequence'),
            # 'refund_sequence_number_next':data.get('refund_sequence_number_next'),
            'sequence':data.get('sequence'),
            # 'sequence_number_next':data.get('sequence_number_next'),
            'show_on_dashboard':data.get('show_on_dashboard'),
            'type':data.get('type').get('sh_api_current_state'),
            # 'update_posted':data.get('update_posted'),
            
        }
        # =========== CHECK CONTROL ACCOUNT EXIST OR NOT PREPARE VALUES FOR THAT ================
        
        if data.get('account_control_ids'):
            account_control_list=[]
            for account in data.get('account_control_ids'):
                if account.get('id') and account.get('id')!=0:
                    domain=['|',('remote_account_account_id','=',account.get('id')),('name','=',account.get('name'))]
                    find_account=self.env['account.account'].search(domain)
                    if find_account:
                        account_control_list.append((4,find_account.id))
                    else:
                        account_vals=self.process_account_account_data(account)            
                        if account_vals:
                            created_account=self.env['account.account'].create(account_vals)
                            if created_account:
                                account_control_list.append((4,created_account.id))
            
            if account_control_list:
                account_journal_vals['account_control_ids']=account_control_list
        # =============== CHECK RES PARTNER BANK EXIST OR NOT IF EXIST THEN RETURN ELSE CREATE AND RETURN =========
               
        if data.get('bank_account_id') and data.get('bank_account_id').get('id') and data.get('bank_account_id').get('id')!=0:
            domain=['|',('remote_res_partner_bank_id','=',data.get('bank_account_id').get('id')),('name','=',data.get('bank_account_id').get('name'))]
            find_res_bank=self.env['res.partner.bank'].search(domain)
            if find_res_bank:
                account_journal_vals['bank_account_id']=find_res_bank.id
            else:
                res_bank_vals=self.process_res_partner_bank_data(data.get('bank_account_id'))
                if res_bank_vals:
                    created_res_bank=self.env['res.partner.bank'].create(res_bank_vals)
                    if created_res_bank:
                        account_journal_vals['bank_account_id']=created_res_bank.id  
        # =============== CHECK RES BANK EXIST OR NOT IF EXIST THEN RETURN ELSE CREATE AND RETURN =========
        if data.get('bank_id'):
            domain=['|',('remote_res_bank_id','=',data.get('bank_id').get('id')),('name','=',data.get('bank_id').get('name'))]
            find_res_bank=self.env['res.bank'].search(domain)
            if find_res_bank:
                account_journal_vals['bank_id']=find_res_bank.id
            else:
                res_bank_vals=self.process_res_bank_data(data.get('bank_id'))
                if res_bank_vals:
                    created_res_bank=self.env['res.bank'].create(res_bank_vals)
                    if created_res_bank:
                        account_journal_vals['bank_id']=created_res_bank.id  
        # # ================== CHECK DEFAULT CREDIT ACCOUNT EXIST OR NOT ===================
        # if data.get('default_credit_account_id') and data.get('default_credit_account_id').get('id') and data.get('default_credit_account_id').get('id')!=0:
        #     domain=['|',('remote_account_account_id','=',data.get('default_credit_account_id').get('id')),('name','=',data.get('default_credit_account_id').get('name'))]
        #     find_account=self.env['account.account'].search(domain)
        #     if find_account:
        #         account_journal_vals['default_credit_account_id']=find_account.id

        #     else:
        #         account_vals=self.process_account_account_data(data.get('default_credit_account_id'))            
        #         if account_vals:
        #             created_account=self.env['account.account'].create(account_vals)
        #             if created_account:
        #                 account_journal_vals['default_credit_account_id']=created_account.id    
        
        #  # ================== CHECK DEFAULT DEBIT ACCOUNT EXIST OR NOT ===================
        # if data.get('default_debit_account_id') and data.get('default_debit_account_id').get('id') and data.get('default_debit_account_id').get('id')!=0:
        #     domain=['|',('remote_account_account_id','=',data.get('default_debit_account_id').get('id')),('name','=',data.get('default_debit_account_id').get('name'))]
        #     find_account=self.env['account.account'].search(domain)
        #     if find_account:
        #         account_journal_vals['default_debit_account_id']=find_account.id

        #     else:
        #         account_vals=self.process_account_account_data(data.get('default_debit_account_id'))            
        #         if account_vals:
        #             created_account=self.env['account.account'].create(account_vals)
        #             if created_account:
        #                 account_journal_vals['default_debit_account_id']=created_account.id    
        
        # ================== CHECK INBOUT PAYMENT METHOD EXIST OR NOT ===================
        # if data.get('inbound_payment_method_ids'):
        #     payment_method_list=[]
        #     for payment_method in data.get('inbound_payment_method_ids'):
        #         domain=['|',('remote_account_payment_method_id','=',payment_method.get('id')),('code','=',payment_method.get('code'))]
        #         find_payment_method=self.env['account.payment.method'].search(domain,limit=1)
        #         if find_payment_method:
        #             payment_method_list.append((4,find_payment_method.id))
        #         else:
        #             payment_method_vals={
        #                 'remote_account_payment_method_id':payment_method.get('id'),
        #                 'code':payment_method.get('code'),
        #                 'name':payment_method.get('name'),
        #                 'display_name':payment_method.get('display_name'),
        #                 'payment_type':payment_method.get('payment_type').get('sh_api_current_state'),
        #             }
        #             if payment_method_vals:
        #                 created_payment_method=self.env['account.payment.method'].create(payment_method_vals)
        #                 if created_payment_method:
        #                     payment_method_list.append((4,created_payment_method.id))
        #     if payment_method_list:
        #         account_journal_vals['inbound_payment_method_ids']=payment_method_list
                
        # =============== CHECK LOSS ACCOUNT EXIST OR NOT ====================
        if data.get('loss_account_id') and data.get('loss_account_id').get('id') and data.get('loss_account_id').get('id')!=0:
            domain=['|',('remote_account_account_id','=',data.get('loss_account_id').get('id')),('name','=',data.get('loss_account_id').get('name'))]
            find_account=self.env['account.account'].search(domain)
            if find_account:
                account_journal_vals['loss_account_id']=find_account.id

            else:
                account_vals=self.process_account_account_data(data.get('loss_account_id'))            
                if account_vals:
                    created_account=self.env['account.account'].create(account_vals)
                    if created_account:
                        account_journal_vals['loss_account_id']=created_account.id 
        # ================== CHECK OUTBOUND PAYMENT METHOD EXIST OR NOT ===================
        # if data.get('outbound_payment_method_ids'):
        #     payment_method_list=[]
        #     for payment_method in data.get('outbound_payment_method_ids'):
        #         domain=['|',('remote_account_payment_method_id','=',payment_method.get('id')),('code','=',payment_method.get('code'))]
        #         find_payment_method=self.env['account.payment.method'].search(domain,limit=1)
        #         if find_payment_method:
        #             payment_method_list.append((4,find_payment_method.id))
        #         else:
        #             payment_method_vals={
        #                 'remote_account_payment_method_id':payment_method.get('id'),
        #                 'code':payment_method.get('code'),
        #                 'name':payment_method.get('name'),
        #                 'display_name':payment_method.get('display_name'),
        #                 'payment_type':payment_method.get('payment_type').get('sh_api_current_state'),
        #             }
        #             if payment_method_vals:
        #                 created_payment_method=self.env['account.payment.method'].create(payment_method_vals)
        #                 if created_payment_method:
        #                     payment_method_list.append((4,created_payment_method.id))
        #     if payment_method_list:
        #         account_journal_vals['outbound_payment_method_ids']=payment_method_list
        
        # =============== CHECK PROFIT ACCOUNT EXIST OR NOT ====================
        if data.get('profit_account_id') and data.get('profit_account_id').get('id') and data.get('profit_account_id').get('id')!=0:
            domain=['|',('remote_account_account_id','=',data.get('profit_account_id').get('id')),('name','=',data.get('profit_account_id').get('name'))]
            find_account=self.env['account.account'].search(domain)
            if find_account:
                account_journal_vals['profit_account_id']=find_account.id
            else:
                account_vals=self.process_account_account_data(data.get('profit_account_id'))            
                if account_vals:
                    created_account=self.env['account.account'].create(account_vals)
                    if created_account:
                        account_journal_vals['profit_account_id']=created_account.id 
        
        return account_journal_vals  
    
    def process_account_payment_data(self,data):        
        ''' ============== PREPARE VALUES FOR IMPORT ACCOUNT PAYMENT WHICH ARE CONNECTED WITH INVOICE ============== '''

        payment_vals={
            'remote_account_payment_id':data.get('id'),
            'amount':data.get('amount'),
            'ref':data.get('communication'),
            'display_name':data.get('display_name'),
            # 'has_invoices':data.get('has_invoices'),
            # 'hide_data_method':data.get('hide_data_method'),
            # 'is_refund_pos':data.get('is_refund_pos'),
            # 'move_name':data.get('move_name'),
            # 'move_reconciled':data.get('move_reconciled'),
            # 'multi':data.get('multi'),
            'name':data.get('name'),
            'partner_type':data.get('partner_type').get('sh_api_current_state'),
            # 'payment_difference':data.get('payment_difference'),
            # 'payment_difference_handling':data.get('payment_difference_handling'),
            'payment_reference':data.get('payment_reference'),
            # 'payment_token_id':data.get('payment_token_id'),
            'payment_type':data.get('payment_type').get('sh_api_current_state'),
            # 'report_token':data.get('report_token'),
            'show_partner_bank_account':data.get('show_partner_bank_account'),
            'state':data.get('state').get('sh_api_current_state'),
            # 'text_message':data.get('text_message'),
            # 'writeoff_label':data.get('writeoff_label'),
            # 'payment_method_line_id':7,
            'payment_method_code':data.get('payment_method_code'),      
            'invoice_ids':data.get('invoice_ids'),       
        }
        if data.get('payment_date'):
            date_time=datetime.strptime(data.get('payment_date'),'%Y-%m-%d')
            payment_vals['date']=date_time

        # ============== Check cashier is exist or not if exist then return else create ==============
        if data.get('cashier'):
            domain_by_id = [('remote_user_id','=',data['cashier']['id'])]
            find_user_id=self.env['res.users'].search(domain_by_id)
            domain_by_login = [('login','=',data['cashier']['login'])]
            find_user_login=self.env['res.users'].search(domain_by_login)
            if find_user_id:
                payment_vals['user_id']=find_user_id.id 
            elif find_user_login:
                payment_vals['user_id']=find_user_login.id 
            else:
                user_vals=self.process_user_data(data['cashier'])
                if user_vals:
                    user_id=self.env['res.users'].sudo().create(user_vals)
                    if user_id:
                        payment_vals['user_id']=user_id.id
            
        # # =========== Mapped Destination account with name or id if not match any then create new account ============
        # if data.get('destination_account_id') and data.get('destination_account_id').get('id') and data.get('destination_account_id').get('id')!=0:
        #     domain=['|',('remote_account_account_id','=',data.get('destination_account_id').get('id')),('name','=',data.get('destination_account_id').get('name'))]
        #     find_account=self.env['account.account'].search(domain)
        #     if find_account:
        #         payment_vals['destination_account_id']=find_account.id

        #     else:
        #         account_vals=self.process_account_account_data(data.get('destination_account_id'))            
        #         if account_vals:
        #             created_account=self.env['account.account'].create(account_vals)
        #             if created_account:
        #                 payment_vals['destination_account_id']=created_account.id
        
        # ============ Connect Journal with Payment if already exist then return otherwise create ====================
        if data.get('destination_journal_id') and data.get('destination_journal_id').get('id') and data.get('destination_journal_id').get('id')!=0:
            domain=['|',('remote_account_journal_id','=',data.get('destination_journal_id').get('id')),('code', '=', data['destination_journal_id']['code']),('type', '=', data['destination_journal_id']['type']['sh_api_current_state'])]
            find_journal=self.env['account.journal'].search(domain)
            if find_journal:
                payment_vals['destination_journal_id']=find_journal.id
            else:
                journal_vals=self.process_account_journal_data(data.get('destination_journal_id'))
                if journal_vals:
                    created_journal = self.env['account.journal'].create(journal_vals)
                    if created_journal:
                        payment_vals['destination_journal_id']=created_journal.id
        
        # ============ Connect Journal with Payment if already exist then return otherwise create ====================
        if data.get('journal_id') and data.get('journal_id').get('id') and data.get('journal_id').get('id')!=0:
            domain=['|',('remote_account_journal_id','=',data.get('journal_id').get('id')),('code', '=', data['journal_id']['code']),('type', '=', data['journal_id']['type']['sh_api_current_state'])]
            find_journal=self.env['account.journal'].search(domain)
            if find_journal:
                payment_vals['journal_id']=find_journal.id
            else:
                journal_vals=self.process_account_journal_data(data.get('journal_id'))
                if journal_vals:
                    created_journal = self.env['account.journal'].create(journal_vals)
                    if created_journal:
                        payment_vals['journal_id']=created_journal.id
        
        
        # ================= CHECK PAYMENT METHOD WHICH IS CONNECTED WITH ACCOUNT PAYMENT =============
        if data.get('payment_method_id'):
            domain=['|',('remote_account_payment_method_id','=',data.get('payment_method_id').get('id')),('code','=',data.get('payment_method_id').get('code'))]
            find_payment_method=self.env['account.payment.method'].search(domain,limit=1)
            if find_payment_method:
                payment_vals['payment_method_id']=find_payment_method.id
            else:
                payment_method_vals={
                    'remote_account_payment_method_id':data.get('payment_method_id').get('id'),
                    'code':data.get('payment_method_id').get('code'),
                    'name':data.get('payment_method_id').get('name'),
                    'display_name':data.get('payment_method_id').get('display_name'),
                    'payment_type':data.get('payment_method_id').get('payment_type').get('sh_api_current_state'),
                }
                if payment_method_vals:
                    created_payment_method=self.env['account.payment.method'].create(payment_method_vals)
                    if created_payment_method:
                        payment_vals['payment_method_id']=created_payment_method.id
                        
        # =========== Mapped Writeoff account with name or id if not match any then create new account ============
        # if data.get('writeoff_account_id') and data.get('writeoff_account_id').get('id') and data.get('writeoff_account_id').get('id')!=0:
        #     domain=['|',('remote_account_account_id','=',data.get('writeoff_account_id').get('id')),('name','=',data.get('writeoff_account_id').get('name'))]
        #     find_account=self.env['account.account'].search(domain)
        #     if find_account:
        #         payment_vals['writeoff_account_id']=find_account.id

            # else:
            #     account_vals=self.process_account_account_data(data.get('writeoff_account_id'))            
            #     if account_vals:
            #         created_account=self.env['account.account'].create(account_vals)
            #         if created_account:
            #             payment_vals['writeoff_account_id']=created_account.id   
            
        
        # ========== CHECK CONNCTED PARTNER IS EXIST OR NOT  =====================
        if data.get('partner_id'):
            domain = [('remote_partner_id', '=', data['partner_id']['id'])]
            find_customer = self.env['res.partner'].search(domain)
            if find_customer:
                payment_vals['partner_id'] = find_customer.id
                print("\n\n===222====find_customer",find_customer)
            else:
                contact_vals=self.process_contact_data(data['partner_id'])
                partner_id=self.env['res.partner'].create(contact_vals)
                if partner_id:
                    payment_vals['partner_id']=partner_id.id
        
        if payment_vals.get('journal_id') and payment_vals.get('payment_method_id')  :
            
            self._cr.execute('''select id from account_payment_method_line where journal_id = %s and payment_method_id = %s ''',
                [payment_vals.get('journal_id'),payment_vals.get('payment_method_id')])
            payment_method_line = self._cr.dictfetchall()    
            
            if payment_method_line:
                payment_vals['payment_method_line_id']=payment_method_line[0].get('id')    
                
        return payment_vals
                        