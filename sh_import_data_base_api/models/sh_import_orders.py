# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields,models,_
import requests
import json
from datetime import datetime
import time

class InheritImportBase(models.Model):
    _inherit = "sh.import.base"
    
    import_order=fields.Boolean("Import Orders")
    records_per_page_so = fields.Integer("No of records per page")
    current_import_page_so = fields.Integer("Current Page",default=0)    
    
    sh_import_filter_order=fields.Boolean("Import Filtered Orders")
    sh_from_date=fields.Datetime("From Date")
    sh_to_date=fields.Datetime("To Date")
    sh_import_order_ids=fields.Char("Order ids")
    
    def import_order_filtered_to_queue(self):
        ''' ========== Import Filtered Ordered 
        between from date and end date ==================  ''' 
        confid = self.env['sh.import.base'].search([],limit=1)  
        if confid.sh_import_filter_order:
            response = requests.get('''%s/api/public/sale.order?query={id,write_date}&filter=[["write_date",">=","%s"],["write_date","<=","%s"]]''' 
                %(confid.base_url,str(confid.sh_from_date),str(confid.sh_to_date)))
            response_json = response.json()
            if response_json.get('result'):
                confid.sh_import_order_ids=[r['id'] for r in response_json.get('result')]
                
    
    def import_order_from_queue(self):
        ''' ========== Import Filtered Ordered 
        between from date and end date ==================  ''' 
        confid = self.env['sh.import.base'].search([],limit=1)  
        if confid.sh_import_filter_order and confid.sh_import_order_ids:   
            orders = confid.sh_import_order_ids.strip('][').split(', ') 
            count=0
            failed=0  
            for order in orders[0:10]:
                try :
                    response = requests.get('''%s/api/public/sale.order/%s?query=
                    {id,name,state,date_order,effective_date,expected_date,validity_date,invoice_status,currency_id,note,amount_untaxed,amount_tax,amount_total,company_id,team_id,access_url,pricelist_id{name,active,display_name},order_line{id,name,invoice_lines,state,qty_to_invoice,is_downpayment,untaxed_amount_to_invoice,related_delivery_status,display_type,invoice_status,price_unit,price_subtotal,price_tax,price_total,price_reduce,qty_delivered,qty_invoiced,qty_to_invoice,discount,product_uom_qty,product_uom,order_id,tax_id{name,amount,type_tax_use},product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}},warehouse_id{id,name,code},partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
                    invoice_ids{number,origin,payment_ids,payment_move_line_ids{payment_id,invoice_id},state,date,date_due,date_invoice,amount_tax,amount_total,amount_total_signed,amount_untaxed,residual,type,id,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},journal_id{id,type,code},invoice_line_ids{*,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
                    invoice_line_tax_ids{name,amount,type_tax_use},product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}}}
                    ,user_id{id,active,active_partner,alias_contact,allow_create_order_line,allow_delete_order,allow_discount,allow_edit_price,allow_manual_customer_selecting,allow_payments,allow_refund,allow_refund,barcode,city,color,comment,contact_address,country_id{name},credit,lang,login,mobile,name,new_password,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},credit_limit,customer,customer_credit,customer_credit_limit,debit,debit_limit,delivery_instructions,delivery_terms,display_name,email,email_formatted,
                    password,phone,state,state_id{name},street,street2,supplier,type,vat,tz,tz_offset}
                    ,picking_ids{name,id,date,date_done,scheduled_date,state,location_id,location_dest_id,picking_type_id{id,name,code},backorder_ids,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},move_ids_without_package{name,id,picking_id,is_locked,is_quantity_done_editable,quantity_done,product_uom_qty,price_unit,state,location_id,location_dest_id,product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}}}}
                    ''' %(confid.base_url,order))
                    response_json = response.json()      
                    if response.status_code==200:
                        for data in response_json.get('result'):
                            domain = ['|',('remote_order_id', '=', data['id']),('name', '=', data['name'])]
                            already_order = self.env['sale.order'].search(domain)
                            # try:
                            created_invoice=False
                            created_order=False
                            payment_list=[]
                            credit_note=[]
                            
                            # order_vals = confid.process_order_data(data)
                            # ======================================================
                            # CREATE SALE ORDER IN DRAFT STATGE IF ORDER NOT EXIST
                            # ======================================================
                            try:
                                # if not already_order:
                                
                                # ======================================================
                                # CHECK SALE ORDER HAS INVOICE,PAYMENT EXIST THEN PREPARE 
                                # DATA FOR CONNCTED INVOICE ,PAYMENT
                                # ======================================================
                                
                                if data.get('picking_ids') or data.get('invoice_ids'):
                                    order_state=data.get('state').get('sh_api_current_state')
                                    order_vals = confid.process_order_data(data)
                                    is_remaining_invoice=False
                                    invoice_ids=[]
                                    invoice_dict={}
                                    if data.get('invoice_ids'):  
                                        for invoice in data.get('invoice_ids'):
                                            invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                            if invoice.get('state').get('sh_api_current_state') not in ['paid','cancel'] or already_order or order_state != 'cancel':
                                                is_remaining_invoice=True     
                                        if is_remaining_invoice:
                                            invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))
                                            for invoice in invoice_list:
                                                invoice_id=self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])                                        
                                                if not invoice_id:
                                                    if invoice[2].get('state'):
                                                        invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                        del invoice[2]['state']
                                                    created_invoice=self.env['account.move'].create(invoice[2])
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
                                                    created_invoice=invoice_id
                                                if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                                    created_invoice.action_post()
                                                elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                                    created_invoice.button_cancel()
                                                if created_invoice.move_type=='out_refund':
                                                    credit_note.append(created_invoice)
                                                elif created_invoice.move_type=='out_invoice':
                                                    invoice_ids.append(created_invoice)      
                                            
                                    is_remaining_picking=False
                                    # ======================================================
                                    # CHECK SALE ORDER HAS STOCK PICKING EXIST THEN PREPARE 
                                    # DATA FOR CONNCTED PICKING
                                    # ======================================================
                                    
                                    if data.get('picking_ids'):
                                        for picking in data.get('picking_ids'):
                                            if picking.get('state').get('sh_api_current_state') not in ['done','cancel'] or already_order  or order_state != 'cancel':
                                                is_remaining_picking=True
                                        if is_remaining_picking or invoice_ids:
                                            order_vals['picking_ids']=[]
                                            picking_list=confid.process_picking_data(data.get('picking_ids'),order_vals.get('warehouse_id'))
                                            for pick in picking_list:
                                                picking_id=self.env['stock.picking'].search([('remote_picking_id','=',pick[2].get('remote_picking_id'))])
                                                if not picking_id:
                                                    order_vals['picking_ids'].append(pick)
                                                else:
                                                    picking_id.action_picking_draft()
                                                    picking_id.write(pick[2])
                                                    order_vals['picking_ids'].append((4,picking_id.id))
                                                    
                                    # ======================================================
                                    # IF SALE ORDER HAS PICKING AND PICKING REMINING FOR 
                                    # DONE THEN CREATE THAT 
                                    # ======================================================
                                    if is_remaining_picking and  order_vals.get('picking_ids') : 
                                        
                                        # ========== CREATE SALE ORDER =======================
                                        order_id=self.env['sale.order'].search(['|',('remote_order_id', '=', order_vals['remote_order_id']),('name', '=', order_vals['name'])])
                                        if not order_id:
                                            created_order = self.env['sale.order'].create(order_vals)
                                            count+=1  
                                        else:
                                            order_id.write(order_vals) 
                                            created_order =order_id                                
                                            
                                        order_state=data.get('state').get('sh_api_current_state')
                                        if created_order and order_state and order_state!=created_order.state:
                                            self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])        
                                        if data.get('date_order'):
                                            date_time=datetime.strptime(data.get('date_order'),'%Y-%m-%d-%H-%M-%S')
                                            date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                                            self.env.cr.execute(''' UPDATE sale_order set date_order=%s where id=%s''', [str(date_time),created_order.id])
                                        if created_order.order_line and created_order.picking_ids:
                                            for line in created_order.order_line:
                                                moves=self.env['stock.move'].search([('product_id','=',line.product_id.id),('picking_id','in',created_order.picking_ids.ids)])
                                                if moves:
                                                    self.env.cr.execute(''' UPDATE stock_move set sale_line_id=%s where id IN %s ''', [line.id,tuple(moves.ids)])

                                        # ======================================================
                                        # IF SALE ORDER HAS INVOICE AND THAT REMANING FOR 
                                        # PAYMENT THEN NEED TO IMPORT THAT 
                                        # ======================================================
                                        if not invoice_ids:
                                            for invoice in data.get('invoice_ids'):
                                                invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                                if invoice.get('state').get('sh_api_current_state') not in ['cancel'] or already_order:
                                                    is_remaining_invoice=True     
                                            if is_remaining_invoice:
                                                invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))
                                                for invoice in invoice_list:
                                                    invoice_id=self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])                                        
                                                    if not invoice_id:
                                                        if invoice[2].get('state'):
                                                            invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                            del invoice[2]['state']
                                                        created_invoice = self.env['account.move'].create(invoice[2])
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
                                                        created_invoice =invoice_id
                                                    if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                                        created_invoice.action_post()
                                                    elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                                        created_invoice.button_cancel()
                                                    if created_invoice.move_type=='out_refund':
                                                        credit_note.append(created_invoice)
                                                    elif created_invoice.move_type=='out_invoice':
                                                        invoice_ids.append(created_invoice)
                                                    
                                        # ======================================================
                                        # CONNECT SALE ORDER AND INVOICE ( CREATE ENTRY OF 
                                        # MANY2MANY TABLE sale_order_line_invoice_rel)
                                        # ======================================================            
                                                    
                                        for invoice in data.get('invoice_ids'):
                                            for invoice_line in invoice.get('invoice_line_ids'):
                                                sale_lines=invoice_line.get("sale_line_ids")
                                                invoice_line_id=invoice_line.get('id')
                                                invoice_line = self.env['account.move.line'].search([('remote_account_move_line_id','=',invoice_line_id)])        
                                                if invoice_line:
                                                    for line in sale_lines:
                                                        related_soline = self.env['sale.order.line'].search([('remote_order_line_id','=',line)])        
                                                        if related_soline:
                                                            self._cr.execute(""" SELECT * FROM sale_order_line_invoice_rel account
                                                                WHERE invoice_line_id=%s and order_line_id=%s """,
                                                                [invoice_line.id,related_soline.id])
                                                            conncted_line=self._cr.fetchall()
                                                            if not conncted_line:
                                                                self.env.cr.execute(""" INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id) VALUES (%s, %s);""" , [invoice_line.id,related_soline.id])
                                                                self.env.cr.commit()     
                                                            related_soline.state=related_soline.order_id.state
                                                            related_soline._compute_qty_invoiced()
                                                            related_soline._compute_invoice_status()
                                                            related_soline.order_id._compute_invoice_status() 
                                                                    
                                    # ============ CHECK INVOICE NEED TO IMPORT OR NOT  ====================                
                                                    
                                    elif is_remaining_invoice and  invoice_ids:
                                        order_id = self.env['sale.order'].search(['|',('remote_order_id', '=', order_vals['remote_order_id']),('name', '=', order_vals['name'])])
                                        if not order_id :
                                            created_order = self.env['sale.order'].create(order_vals)
                                            count+=1
                                        else:
                                            order_id.write(order_vals)
                                            created_order = order_id
                                        order_state=data.get('state').get('sh_api_current_state')
                                        if created_order and order_state and order_state!=created_order.state:
                                            self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])        
                                        if data.get('date_order'):
                                            date_time=datetime.strptime(data.get('date_order'),'%Y-%m-%d-%H-%M-%S')
                                            date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                                            self.env.cr.execute(''' UPDATE sale_order set date_order=%s where id=%s''', [str(date_time),created_order.id])
                                        if created_order.order_line and created_order.picking_ids:
                                            for line in created_order.order_line:
                                                moves=self.env['stock.move'].search([('product_id','=',line.product_id.id),('picking_id','in',created_order.picking_ids.ids)])
                                                if moves:
                                                    self.env.cr.execute(''' UPDATE stock_move set sale_line_id=%s where id IN %s ''', [line.id,tuple(moves.ids)])
                                        
                                        # ======================================================
                                        # IF SALE ORDER HAS INVOICE AND THAT REMANING FOR 
                                        # PAYMENT THEN NEED TO IMPORT THAT 
                                        # ======================================================
                                        
                                        if not invoice_ids:
                                            for invoice in data.get('invoice_ids'):
                                                invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                                if invoice.get('state').get('sh_api_current_state') not in ['cancel'] or already_order:
                                                    is_remaining_invoice=True     
                                            if is_remaining_invoice:
                                                invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))
                                                for invoice in invoice_list:
                                                    invoice_id = self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])
                                                    if not invoice_id:
                                                        if invoice[2].get('state'):
                                                            invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                            del invoice[2]['state']
                                                        created_invoice = self.env['account.move'].create(invoice[2])
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
                                                        created_invoice=invoice_id
                                                    if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                                        created_invoice.action_post()
                                                    elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                                        created_invoice.button_cancel()
                                                    if created_invoice.move_type=='out_refund':
                                                        credit_note.append(created_invoice)
                                                    elif created_invoice.move_type=='out_invoice':
                                                        invoice_ids.append(created_invoice)                                    
                                                
                                        # ======================================================
                                        # CONNECT SALE ORDER AND INVOICE ( CREATE ENTRY ON 
                                        # MANY2MANY TABLE sale_order_line_invoice_rel)
                                        # ======================================================               
                                        for invoice in data.get('invoice_ids'):
                                            for invoice_line in invoice.get('invoice_line_ids'):
                                                sale_lines=invoice_line.get("sale_line_ids")
                                                invoice_line_id=invoice_line.get('id')
                                                invoice_line = self.env['account.move.line'].search([('remote_account_move_line_id','=',invoice_line_id)])        
                                                if invoice_line:
                                                    for line in sale_lines:
                                                        related_soline = self.env['sale.order.line'].search([('remote_order_line_id','=',line)])        
                                                        if related_soline:
                                                            self._cr.execute(""" SELECT * FROM sale_order_line_invoice_rel account
                                                                WHERE invoice_line_id=%s and order_line_id=%s """,
                                                                [invoice_line.id,related_soline.id])
                                                            conncted_line=self._cr.fetchall()
                                                            if not conncted_line:
                                                                self.env.cr.execute(""" INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id) VALUES (%s, %s);""" , [invoice_line.id,related_soline.id])
                                                                self.env.cr.commit()        
                                                            related_soline.state=related_soline.order_id.state
                                                            related_soline._compute_qty_invoiced()
                                                            related_soline._compute_invoice_status()
                                                            related_soline.order_id._compute_invoice_status()  
                                    
                                    # ======================================================
                                    # CONNECT INVOICE AND PAYMENT ( INVOICE AND PAYMENT 
                                    # JOURNAL ENTRY RECONCILE )
                                    # ====================================================== 
                                    connected_invoice_ids=[]
                                    
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
                                
                                else:   
                                    # =====================================================
                                    # CREATE OR UPDATE QUOTATION AND QUOTATION SENT ORDER 
                                    # =====================================================
                                    
                                    order_vals = confid.process_order_data(data)
                                    order_state=data.get('state').get('sh_api_current_state')
                                    if order_state and order_state != 'cancel':
                                        if already_order:
                                            already_order.write(order_vals)
                                            order_state=data.get('state').get('sh_api_current_state')
                                            if already_order and order_state and order_state!=already_order.state:
                                                self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,already_order.id]) 
                                        else:
                                            created_order=self.env['sale.order'].create(order_vals) 
                                            count+=1
                                            order_state=data.get('state').get('sh_api_current_state')
                                            if created_order and order_state and order_state!=created_order.state:
                                                self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])        
                                
                            except Exception as e:
                                failed += 1
                                vals = {
                                    "name": order,
                                    "error": e,
                                    "field_type": "order",                           
                                    "datetime": datetime.now(),
                                    "base_config_id": confid.id,
                                }
                                self.env['sh.import.failed'].create(vals)

                    else:
                        failed += 1
                        vals = {
                            "name": confid.name,
                            "state": "error",
                            "field_type": "order",
                            "error": response.text,
                            "datetime": datetime.now(),
                            "base_config_id": confid.id,
                            "operation": "import"
                        }
                        self.env['sh.import.base.log'].create(vals)
                        
                    
                except Exception as e:
                    failed += 1
                    vals = {
                        "name": order,
                        "error": e,
                        "field_type": "order",                           
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                    }
                    self.env['sh.import.failed'].create(vals)
            confid.sh_import_order_ids='['+', '.join([str(elem) for elem in orders[10:]])+']'
            
            if count > 0:              
                vals = {
                    "name": confid.name,
                    "state": "success",
                    "field_type": "order",
                    "error": "%s Order Update Successfully" %(count),
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)
            if failed > 0:
                vals = {
                    "name": confid.name,
                    "state": "error",
                    "field_type": "order",
                    "error": "%s Failed To Update" %(failed),
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)    
            
    def import_orders_cron(self):   
        ''' ========== Import Sale_orders ==================  '''
        confid = self.env['sh.import.base'].search([],limit=1)
        if confid.import_order:
            confid.current_import_page_so += 1
            response = requests.get('''%s/api/public/sale.order?query=
            {id,name,state,date_order,effective_date,expected_date,validity_date,invoice_status,currency_id,note,amount_untaxed,amount_tax,amount_total,company_id,team_id,access_url,pricelist_id{name,active,display_name},order_line{id,name,invoice_lines,state,qty_to_invoice,is_downpayment,untaxed_amount_to_invoice,related_delivery_status,display_type,invoice_status,price_unit,price_subtotal,price_tax,price_total,price_reduce,qty_delivered,qty_invoiced,qty_to_invoice,discount,product_uom_qty,product_uom,order_id,tax_id{name,amount,type_tax_use},product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}},warehouse_id{id,name,code},partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
            invoice_ids{number,origin,payment_ids,payment_move_line_ids{payment_id,invoice_id},state,date,date_due,date_invoice,amount_tax,amount_total,amount_total_signed,amount_untaxed,residual,type,id,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},journal_id{id,type,code},invoice_line_ids{*,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},
            invoice_line_tax_ids{name,amount,type_tax_use},product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}}}
            ,user_id{id,active,active_partner,alias_contact,allow_create_order_line,allow_delete_order,allow_discount,allow_edit_price,allow_manual_customer_selecting,allow_payments,allow_refund,allow_refund,barcode,city,color,comment,contact_address,country_id{name},credit,lang,login,mobile,name,new_password,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},credit_limit,customer,customer_credit,customer_credit_limit,debit,debit_limit,delivery_instructions,delivery_terms,display_name,email,email_formatted,
            password,phone,state,state_id{name},street,street2,supplier,type,vat,tz,tz_offset}
            ,picking_ids{name,id,date,date_done,scheduled_date,state,location_id,location_dest_id,picking_type_id{id,name,code},backorder_ids,partner_id{name,vat,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids{name,title,ref,type,website,supplier,street,street2,city,state_id{name},country_id{name},zip,email,is_company,phone,mobile,id,company_type,customer,child_ids}},move_ids_without_package{name,id,picking_id,is_locked,is_quantity_done_editable,quantity_done,product_uom_qty,price_unit,state,location_id,location_dest_id,product_id{id,product_tmpl_id{*,-sh_history_ids,taxes_id{name,amount,type_tax_use},supplier_taxes_id{name,amount,type_tax_use},seller_ids{price,product_code,product_name,min_qty,date_start,date_end,product_uom,name{name,title,ref,type,website,supplier,street,email,is_company,phone,mobile,id,company_type}}}}}}}
            &page_size=%s&page=%s&order="id asc"''' %(confid.base_url,confid.records_per_page_so,confid.current_import_page_so))
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('count') and confid.records_per_page_so != response_json['count']:
                    confid.import_order = False
                    confid.current_import_page_so = 0
                count = 0
                failed = 0
                already_order=False
                for data in response_json.get('result'):
                    domain = ['|',('remote_order_id', '=', data['id']),('name', '=', data['name'])]
                    already_order = self.env['sale.order'].search(domain)
                    # try:
                    created_invoice=False
                    created_order=False
                    payment_list=[]
                    credit_note=[]
                    
                    # order_vals = confid.process_order_data(data)
                    # ======================================================
                    # CREATE SALE ORDER IN DRAFT STATGE IF ORDER NOT EXIST
                    # ======================================================
                    
                    # if not already_order:
                    
                    # ======================================================
                    # CHECK SALE ORDER HAS INVOICE,PAYMENT EXIST THEN PREPARE 
                    # DATA FOR CONNCTED INVOICE ,PAYMENT
                    # ======================================================
                    try:
                        if data.get('picking_ids') or data.get('invoice_ids'):
                            order_state=data.get('state').get('sh_api_current_state')
                            order_vals = confid.process_order_data(data)
                            is_remaining_invoice=False
                            invoice_ids=[]
                            invoice_dict={}
                            if data.get('invoice_ids'):  
                                for invoice in data.get('invoice_ids'):
                                    invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                    if invoice.get('state').get('sh_api_current_state') not in ['paid','cancel'] or already_order or order_state != 'cancel':
                                        is_remaining_invoice=True     
                                if is_remaining_invoice:
                                    invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))
                                    for invoice in invoice_list:
                                        invoice_id=self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])                                        
                                        if not invoice_id:
                                            if invoice[2].get('state'):
                                                invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                del invoice[2]['state']
                                            created_invoice=self.env['account.move'].create(invoice[2])
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
                                            created_invoice=invoice_id
                                        if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                            created_invoice.action_post()
                                        elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                            created_invoice.button_cancel()
                                        if created_invoice.move_type=='out_refund':
                                            credit_note.append(created_invoice)
                                        elif created_invoice.move_type=='out_invoice':
                                            invoice_ids.append(created_invoice)      
                                    
                            is_remaining_picking=False
                            # ======================================================
                            # CHECK SALE ORDER HAS STOCK PICKING EXIST THEN PREPARE 
                            # DATA FOR CONNCTED PICKING
                            # ======================================================
                            
                            if data.get('picking_ids'):
                                for picking in data.get('picking_ids'):
                                    if picking.get('state').get('sh_api_current_state') not in ['done','cancel'] or already_order or order_state != 'cancel':
                                        is_remaining_picking=True
                                if is_remaining_picking or invoice_ids:
                                    order_vals['picking_ids']=[]
                                    picking_list=confid.process_picking_data(data.get('picking_ids'),order_vals.get('warehouse_id'))
                                    for pick in picking_list:
                                        picking_id=self.env['stock.picking'].search([('remote_picking_id','=',pick[2].get('remote_picking_id'))])
                                        if not picking_id:
                                            order_vals['picking_ids'].append(pick)
                                        else:
                                            picking_id.action_picking_draft()
                                            picking_id.write(pick[2])
                                            order_vals['picking_ids'].append((4,picking_id.id))
                                            
                            # ======================================================
                            # IF SALE ORDER HAS PICKING AND PICKING REMINING FOR 
                            # DONE THEN CREATE THAT 
                            # ======================================================
                            if is_remaining_picking and  order_vals.get('picking_ids') : 
                                
                                # ========== CREATE SALE ORDER =======================
                                order_id=self.env['sale.order'].search(['|',('remote_order_id', '=', order_vals['remote_order_id']),('name', '=', order_vals['name'])])
                                if not order_id:
                                    created_order = self.env['sale.order'].create(order_vals)  
                                    count+=1
                                else:
                                    order_id.write(order_vals) 
                                    created_order =order_id                                
                                    
                                order_state=data.get('state').get('sh_api_current_state')
                                if created_order and order_state and order_state!=created_order.state:
                                    self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])        
                                if data.get('date_order'):
                                    date_time=datetime.strptime(data.get('date_order'),'%Y-%m-%d-%H-%M-%S')
                                    date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                                    self.env.cr.execute(''' UPDATE sale_order set date_order=%s where id=%s''', [str(date_time),created_order.id])
                                if created_order.order_line and created_order.picking_ids:
                                    for line in created_order.order_line:
                                        moves=self.env['stock.move'].search([('product_id','=',line.product_id.id),('picking_id','in',created_order.picking_ids.ids)])
                                        if moves:
                                            self.env.cr.execute(''' UPDATE stock_move set sale_line_id=%s where id IN %s ''', [line.id,tuple(moves.ids)])

                                # ======================================================
                                # IF SALE ORDER HAS INVOICE AND THAT REMANING FOR 
                                # PAYMENT THEN NEED TO IMPORT THAT 
                                # ======================================================
                                if not invoice_ids:
                                    for invoice in data.get('invoice_ids'):
                                        invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                        if invoice.get('state').get('sh_api_current_state') not in ['cancel'] or already_order:
                                            is_remaining_invoice=True     
                                    if is_remaining_invoice:
                                        invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))                                    
                                        for invoice in invoice_list:
                                            invoice_id=self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])                                        
                                            if not invoice_id:
                                                if invoice[2].get('state'):
                                                    invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                    del invoice[2]['state']
                                                created_invoice = self.env['account.move'].create(invoice[2])
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
                                                created_invoice =invoice_id
                                            if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                                created_invoice.action_post()
                                            elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                                created_invoice.button_cancel()
                                            if created_invoice.move_type=='out_refund':
                                                credit_note.append(created_invoice)
                                            elif created_invoice.move_type=='out_invoice':
                                                invoice_ids.append(created_invoice)
                                            
                                # ======================================================
                                # CONNECT SALE ORDER AND INVOICE ( CREATE ENTRY OF 
                                # MANY2MANY TABLE sale_order_line_invoice_rel)
                                # ======================================================            
                                            
                                for invoice in data.get('invoice_ids'):
                                    for invoice_line in invoice.get('invoice_line_ids'):
                                        sale_lines=invoice_line.get("sale_line_ids")
                                        invoice_line_id=invoice_line.get('id')
                                        invoice_line = self.env['account.move.line'].search([('remote_account_move_line_id','=',invoice_line_id)])        
                                        if invoice_line:
                                            for line in sale_lines:
                                                related_soline = self.env['sale.order.line'].search([('remote_order_line_id','=',line)])        
                                                if related_soline:
                                                    self._cr.execute(""" SELECT * FROM sale_order_line_invoice_rel account
                                                        WHERE invoice_line_id=%s and order_line_id=%s """,
                                                        [invoice_line.id,related_soline.id])
                                                    conncted_line=self._cr.fetchall()
                                                    if not conncted_line:
                                                        self.env.cr.execute(""" INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id) VALUES (%s, %s);""" , [invoice_line.id,related_soline.id])
                                                        self.env.cr.commit()     
                                                    related_soline.state=related_soline.order_id.state
                                                    related_soline._compute_qty_invoiced()
                                                    related_soline._compute_invoice_status()
                                                    related_soline.order_id._compute_invoice_status() 
                                                            
                            # ============ CHECK INVOICE NEED TO IMPORT OR NOT  ====================                
                                            
                            elif is_remaining_invoice and  invoice_ids:
                                order_id = self.env['sale.order'].search(['|',('remote_order_id', '=', order_vals['remote_order_id']),('name', '=', order_vals['name'])])
                                if not order_id :
                                    created_order = self.env['sale.order'].create(order_vals)
                                    count+=1
                                else:
                                    order_id.write(order_vals)
                                    created_order = order_id
                                order_state=data.get('state').get('sh_api_current_state')
                                if created_order and order_state and order_state!=created_order.state:
                                    self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])        
                                if data.get('date_order'):
                                    date_time=datetime.strptime(data.get('date_order'),'%Y-%m-%d-%H-%M-%S')
                                    date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
                                    self.env.cr.execute(''' UPDATE sale_order set date_order=%s where id=%s''', [str(date_time),created_order.id])
                                if created_order.order_line and created_order.picking_ids:
                                    for line in created_order.order_line:
                                        moves=self.env['stock.move'].search([('product_id','=',line.product_id.id),('picking_id','in',created_order.picking_ids.ids)])
                                        if moves:
                                            self.env.cr.execute(''' UPDATE stock_move set sale_line_id=%s where id IN %s ''', [line.id,tuple(moves.ids)])
                                
                                # ======================================================
                                # IF SALE ORDER HAS INVOICE AND THAT REMANING FOR 
                                # PAYMENT THEN NEED TO IMPORT THAT 
                                # ======================================================
                                
                                if not invoice_ids:
                                    for invoice in data.get('invoice_ids'):
                                        invoice_dict[str(invoice.get('id'))]=invoice.get('state').get('sh_api_current_state')
                                        if invoice.get('state').get('sh_api_current_state') not in ['cancel'] or already_order:
                                            is_remaining_invoice=True     
                                    if is_remaining_invoice:
                                        invoice_list,payment_list=confid.process_invoice_data(data.get('invoice_ids'))
                                        for invoice in invoice_list:
                                            invoice_id = self.env['account.move'].search([('remote_account_move_id','=',invoice[2].get('remote_account_move_id'))])
                                            if not invoice_id:
                                                if invoice[2].get('state'):
                                                    invoice_dict[str(invoice[2].get('remote_account_move_id'))]=invoice[2].get('state')   
                                                    del invoice[2]['state']
                                                created_invoice = self.env['account.move'].create(invoice[2])
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
                                                created_invoice=invoice_id
                                            if invoice_dict[str(created_invoice.remote_account_move_id)] in ['open','in_payment','paid'] and created_invoice.state!='posted':
                                                created_invoice.action_post()
                                            elif invoice_dict[str(created_invoice.remote_account_move_id)] in ['cancel'] and created_invoice.state!='cancel':
                                                created_invoice.button_cancel()
                                            if created_invoice.move_type=='out_refund':
                                                credit_note.append(created_invoice)
                                            elif created_invoice.move_type=='out_invoice':
                                                invoice_ids.append(created_invoice)                                    
                                        
                                # ======================================================
                                # CONNECT SALE ORDER AND INVOICE ( CREATE ENTRY ON 
                                # MANY2MANY TABLE sale_order_line_invoice_rel)
                                # ======================================================               
                                for invoice in data.get('invoice_ids'):
                                    for invoice_line in invoice.get('invoice_line_ids'):
                                        sale_lines=invoice_line.get("sale_line_ids")
                                        invoice_line_id=invoice_line.get('id')
                                        invoice_line = self.env['account.move.line'].search([('remote_account_move_line_id','=',invoice_line_id)])        
                                        if invoice_line:
                                            for line in sale_lines:
                                                related_soline = self.env['sale.order.line'].search([('remote_order_line_id','=',line)])        
                                                if related_soline:
                                                    self._cr.execute(""" SELECT * FROM sale_order_line_invoice_rel account
                                                        WHERE invoice_line_id=%s and order_line_id=%s """,
                                                        [invoice_line.id,related_soline.id])
                                                    conncted_line=self._cr.fetchall()
                                                    if not conncted_line:
                                                        self.env.cr.execute(""" INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id) VALUES (%s, %s);""" , [invoice_line.id,related_soline.id])
                                                        self.env.cr.commit()        
                                                    related_soline.state=related_soline.order_id.state
                                                    related_soline._compute_qty_invoiced()
                                                    related_soline._compute_invoice_status()
                                                    related_soline.order_id._compute_invoice_status()  
                            
                            # ======================================================
                            # CONNECT INVOICE AND PAYMENT ( INVOICE AND PAYMENT 
                            # JOURNAL ENTRY RECONCILE )
                            # ====================================================== 
                            connected_invoice_ids=[]
                            
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
                        
                        else:   
                            # =====================================================
                            # CREATE OR UPDATE QUOTATION AND QUOTATION SENT ORDER 
                            # =====================================================
                        
                            order_vals = confid.process_order_data(data)
                            order_state=data.get('state').get('sh_api_current_state')
                            if order_state and order_state != 'cancel':
                                if already_order:
                                    already_order.write(order_vals)
                                    order_state=data.get('state').get('sh_api_current_state')
                                    if already_order and order_state and order_state!=already_order.state:
                                        self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,already_order.id]) 
                                else:
                                    created_order=self.env['sale.order'].create(order_vals) 
                                    count+=1
                                    order_state=data.get('state').get('sh_api_current_state')
                                    if created_order and order_state and order_state!=created_order.state:
                                        self.env.cr.execute(''' UPDATE sale_order set state=%s where id=%s''', [order_state,created_order.id])         
                        
                    except Exception as e:
                        failed += 1
                        vals = {
                            "name": data['id'],
                            "error": e,
                            "import_json" : data,
                            "field_type": "order",                           
                            "datetime": datetime.now(),
                            "base_config_id": confid.id,
                        }
                        self.env['sh.import.failed'].create(vals)
                if count > 0:              
                    vals = {
                        "name": confid.name,
                        "state": "success",
                        "field_type": "order",
                        "error": "%s Order Imported Successfully" %(count-failed),
                        "datetime": datetime.now(),
                        "base_config_id": confid.id,
                        "operation": "import"
                    }
                    self.env['sh.import.base.log'].create(vals)
                if failed > 0:
                    vals = {
                        "name": confid.name,
                        "state": "error",
                        "field_type": "order",
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
                    "field_type": "order",
                    "error": response.text,
                    "datetime": datetime.now(),
                    "base_config_id": confid.id,
                    "operation": "import"
                }
                self.env['sh.import.base.log'].create(vals)      
                        
    def process_order_line_data(self,data):
        ''' ================= Import sale order lines=============  '''
        order_line_list=[]
        for line in data:
            
            if line.get('display_type') and line.get('display_type').get('sh_api_current_state') and line.get('display_type').get('sh_api_current_state')=='line_section' or line.get('display_type').get('sh_api_current_state')=='line_note':
                line_vals={
                    'remote_order_line_id':line.get('id'),
                    'name':line.get('name'),
                    'display_type':line.get('display_type').get('sh_api_current_state'),
                }
            else:
                line_vals={
                    'remote_order_line_id':line.get('id'),
                    # 'display_type':line.get('display_type').get('sh_api_current_state'),
                    'price_unit':line.get('price_unit'),
                    'price_subtotal':line.get('price_subtotal'),
                    'price_tax':line.get('price_tax'),
                    'price_total':line.get('price_total'),
                    'price_reduce':line.get('price_reduce'),
                    'product_uom_qty':line.get('product_uom_qty'),
                    'qty_delivered':line.get('qty_delivered'),
                    'qty_invoiced':line.get('qty_invoiced'),
                    'qty_to_invoice':line.get('qty_to_invoice'),
                    'discount':line.get('discount'),
                    'name':line.get('name'),
                    'invoice_status':line.get('invoice_status').get('sh_api_current_state'),
                    'state':line.get('state').get('sh_api_current_state'),
                    'is_downpayment':line.get('is_downpayment'),
                    'untaxed_amount_to_invoice':line.get('untaxed_amount_to_invoice'),
                }
                
                # =================  Get Product if created ===================
                if line.get('product_id'):
                    domain = [('remote_product_template_id', '=', line['product_id']['product_tmpl_id']['id'])]
                    find_product = self.env['product.template'].search(domain,limit=1)
                    if find_product:
                        find_product_var = self.env['product.product'].search([('product_tmpl_id','=',find_product.id)],limit=1)
                        if find_product_var:
                            line_vals['product_id'] = find_product_var.id
                        else:
                            product_vals=self.process_product_data(line['product_id']['product_tmpl_id'])
                            product_id=self.env['product.template'].create(product_vals)
                            if product_id:
                                find_product_var = self.env['product.product'].search([('product_tmpl_id','=',product_id.id)],limit=1)
                                if find_product_var:
                                    line_vals['product_id']=find_product_var.id
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
                            else:
                                check_archived_product= self.env['product.product'].search([('product_tmpl_id','=',product_id.id),('active','=',False)],limit=1)
                                line_vals['product_id'] = check_archived_product.id
                                   
                # ==============  Import line tax ===================
                
                if line.get('tax_id'):
                    tax_list = self.process_tax(line['tax_id'])
                    if tax_list:
                        line_vals['tax_id'] = tax_list
            order_line=self.env['sale.order.line'].search([('remote_order_line_id','=',line.get('id'))])
            if order_line:
                order_line.write(line_vals)
            else:
                order_line_list.append((0,0,line_vals))                     
        return order_line_list                
                         
                        
    def process_order_data(self,data):
        ''' ================= Import Orders =============  '''
        order_vals = {
            'remote_order_id':data.get('id'),            
            'currency_id':data.get('currency_id'),
            'x_studio_order_notes':data.get('note').title() if data.get('note') else '',  # Ensure notes are in Leading Capitals
            'name':data.get('name'),
            'amount_untaxed':data.get('amount_untaxed'),
            'amount_tax':data.get('amount_tax'),
            'amount_total':data.get('amount_total'),
            'access_url':data.get('access_url'),
            'invoice_status':data['invoice_status']['sh_api_current_state'] if data.get('invoice_status') else 'no',
        }
        # ======== Get partner if already created or create ==========
        
        # Validate and parse the date_order from the provided data
        date_order = data.get('date_order')
        try:
            date_time = datetime.strptime(date_order, '%Y-%m-%d-%H-%M-%S')
            # Check if the parsed date_order is not in the future
            if date_time > datetime.now():
                raise ValueError("The date_order is in the future.")
        except (ValueError, TypeError):
            self.env['sh.import.base.log'].create({
                "name": "Invalid date_order",
                "state": "error",
                "field_type": "order",
                "error": "Invalid or future date_order provided: {}".format(date_order),
                "datetime": datetime.now(),
                "base_config_id": self.id,
                "operation": "import"
            })
            # Set to a default past date or take other appropriate action
            date_time = datetime.now()  # This line can be adjusted to set a different default date
        order_vals['date_order'] = date_time.strftime('%Y-%m-%d %H:%M:%S')
        
        if data.get('effective_date'):
            date_time=datetime.strptime(data.get('effective_date'),'%Y-%m-%d')
            order_vals['effective_date']=date_time
            
        if data.get('expected_date'):
            date_time=datetime.strptime(data.get('expected_date'),'%Y-%m-%d-%H-%M-%S')
            date_time=date_time.strftime('%Y-%m-%d %H:%M:%S')
            order_vals['expected_date']=date_time
            
        if data.get('validity_date'):
            date_time=datetime.strptime(data.get('validity_date'),'%Y-%m-%d')
            order_vals['validity_date']=date_time

        if data.get('partner_id'):
            domain = [('remote_partner_id', '=', data['partner_id']['id'])]
            find_customer = self.env['res.partner'].search(domain)
            if find_customer:
                order_vals['partner_id'] = find_customer.id
            else:
                contact_vals=self.process_contact_data(data['partner_id'])
                partner_id=self.env['res.partner'].create(contact_vals)
                if partner_id:
                    order_vals['partner_id']=partner_id.id
                
        if data.get('user_id'):
            domain_by_id = [('remote_user_id','=',data['user_id']['id'])]
            find_user_id=self.env['res.users'].search(domain_by_id)
            domain_by_login = [('login','=',data['user_id']['login'])]
            find_user_login=self.env['res.users'].search(domain_by_login)
            if find_user_id:
                order_vals['user_id']=find_user_id.id 
            elif find_user_login:
                order_vals['user_id']=find_user_login.id 
            else:
                user_vals=self.process_user_data(data['user_id'])
                if user_vals:
                    user_id=self.env['res.users'].sudo().create(user_vals)
                    if user_id:
                        order_vals['user_id']=user_id.id
        
        # ======== Get Warehouse if already created or create =========
        
        if data.get('warehouse_id'):
            domain_by_id = [('remote_warehouse_id', '=', data['warehouse_id']['id'])]
            find_warehouse_by_id = self.env['stock.warehouse'].search(domain_by_id,
            limit=1
            )
            domain_by_code = [('code', '=', data['warehouse_id']['code'])]
            find_warehouse_by_code = self.env['stock.warehouse'].search(domain_by_code,limit=1)
            if find_warehouse_by_id:
                find_warehouse_by_id.write({
                    'delivery_steps':'pick_ship',
                })
                order_vals['warehouse_id'] = find_warehouse_by_id.id
            elif find_warehouse_by_code:
                find_warehouse_by_code.write({
                    'delivery_steps':'pick_ship',
                })
                order_vals['warehouse_id'] = find_warehouse_by_code.id
            else:
                warehouse_vals=self.process_warehouse_data(data['warehouse_id'])
                warehouse_id=self.env['stock.warehouse'].create(warehouse_vals)
                if warehouse_id:
                    order_vals['warehouse_id']=warehouse_id.id
                            
        # ======= Prepare orderlines ==================
        if data.get('order_line'):
            order_line_list=self.process_order_line_data(data.get('order_line'))
            if order_line_list:
                order_vals['order_line']=order_line_list      
                
        return order_vals

    
