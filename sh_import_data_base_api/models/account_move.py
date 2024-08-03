# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    remote_account_move_id = fields.Char("Remote Invoice ID")
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    remote_account_move_line_id = fields.Char("Remote Invoice line ID")
    
    def _check_reconciliation(self):
        for line in self:
            if line.matched_debit_ids or line.matched_credit_ids:
                print("You cannot do this modification on a reconciled journal entry. "
                    "You can just change some non legal fields or you must unreconcile first.\n")
                    #   "Journal Entry (id): %s (%s)"% (line.move_id.name, line.move_id.id))
    
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    remote_account_payment_id = fields.Char("Remote Invoice Payment ID")
    
class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    remote_account_account_id = fields.Char("Remote Account ID")
    
class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'
    
    remote_account_tag_id = fields.Char("Remote Account Tag ID")
    
    
class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    remote_account_journal_id = fields.Char("Remote Account Journal ID")
    
    
class ResBank(models.Model):
    _inherit = 'res.bank'
    
    remote_res_bank_id = fields.Char("Remote Res Bank ID")

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    remote_res_partner_bank_id = fields.Char("Remote Res Bank ID")
    
class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'
    
    remote_account_payment_method_id = fields.Char("Remote Account Payment Method ID")