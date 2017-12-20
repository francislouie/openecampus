from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
from datetime import date, datetime, timedelta
from dateutil import parser
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    """modify account.invoice"""
    def cumput_old_balance(self, cr, uid, partner):
        balance = 0
        ids_trans = self.pool.get('client.trancations').search(cr, uid, [('partner_id','=',partner)])
        if ids_trans:
            br_cl_reg = self.pool.get('client.trancations').browse(cr,uid,ids_trans)
            dr = 0
            cr = 0
            for history in br_cl_reg:
                dr = dr + history.dr
                cr = cr + history.cr
            balance = dr - cr
        return balance
    
    def calculate_installements(self, cr, uid, ids,context=None):
        for f in self.browse(cr,uid,ids):
            drft_lin_ids = self.pool.get('client.trancations').search(cr,uid,[('invoice_id','=',f.id),('state','=','Draft')])
            date_format = '%Y-%m-%d'
            for i in drft_lin_ids:
                    self.pool.get('client.trancations').unlink(cr,uid,i)
            for i in range(0,f.no_of_instl):
                if i == 0:
                    convert_datetime = datetime.strptime(f.instalment_start_date, date_format)
                    next_day = convert_datetime + timedelta(days=f.days_in_instalment)
                else:
                    next_day = next_day + timedelta(days=f.days_in_instalment)
                    
                self.pool.get('client.trancations').create(cr,uid,{
                        # here vourcher id, or move_id will be the same as move_id for invoice, keep it fields related to accont invoice
                        'name': 'Instalment'+'-'+str(i+1),
                        'invoice_no':str(f.id)+"-("+str(f.name or '--')+")", 
                        'effective_date': f.date_invoice,
                        'due_date': next_day,
                        'partner_id':f.partner_id.id,
                        'amount':f.amount_per_installment,
                        'invoice_id':f.id,
                        'state':'Draft',
                        })
        return
    
    def post_to_register(self, cr, uid, ids,context=None):
        for f in self.browse(cr,uid,ids):
            if f.posted_to_client_reg:
                raise osv.except_osv(('Already Posted To'),(str(f.partner_id.name)+" Register"))
            else: 
                drft_lin_ids = self.pool.get('client.trancations').search(cr,uid,[('invoice_id','=',f.id),('state','=','Draft')])
                for i in drft_lin_ids:
                    posted = self.pool.get('client.trancations').write(cr,uid,i,{'state':'Unpaid'})
                self.write(cr,uid,f.id,{'posted_to_client_reg':True})
        return  
    
    def onchange_installments(self, cr, uid,ids,no_inst,total_amnt):
        result = {}
        if no_inst >0:
            instl = total_amnt/no_inst
            result['amount_per_installment'] = instl
        return {'value':result}
   
    _name = 'account.invoice'
    _inherit ='account.invoice'
    _columns = {
                'posted_to_client_reg':fields.boolean('Posted In Client Register'),
                'create_monthly_installments':fields.boolean('Create monthly installments'),
                'no_of_instl':fields.integer('How Many Installments'),
                'instalment_start_date':fields.date('Installment Start Date'),
                'days_in_instalment':fields.integer('Installment Days'),
                'amount_per_installment':fields.float('Amount Per Installment'),
                'instalments_ids': fields.one2many('client.trancations', 'invoice_id', 'Installments'),
                }
account_invoice()

class res_partner(osv.osv):
    
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
                 'transaction_ids':fields.one2many('client.trancations','partner_id','Transactions'),
                 }
res_partner()

class client_trancations(osv.osv):
    """modify account.invoice"""
    def create(self, cr, uid, vals, context=None, check=True):
        super(osv.osv, self).create(cr, uid, vals, context)
        return True
 
    _name = 'client.trancations'
    _columns = {
                'name': fields.char('Name',size=100),
                'invoice_no': fields.char('Invoice No',size=100), 
                'effective_date': fields.date('Effective Date'),
                'due_date': fields.date('Due Date'), 
                'paid_on':fields.datetime('Paid on'), 
                'instalments_created_by':fields.many2one('res.users','Created By'), 
                'instalment_received_by':fields.many2one('res.users','Received By'), 
                'partner_id':fields.many2one('res.partner','Client'),
                'invoice_id':fields.many2one('account.invoice','Invoice'),
                'amount':fields.float('Amount', digits_compute=dp.get_precision('Amount')),
                'remaining_balance_atthe_time':fields.float('Balance', digits_compute=dp.get_precision('Account')),
                'state':fields.selection([('Draft','Draft'),('Unpaid','Unpaid'),('Paid','Paid'),('Returned','Returned'),('Cancelled','Cancelled')],'State')
                }
client_trancations() 

#--------------------------------------------------------------------------------------------------------------------------------------------------------------__
class account_voucher(osv.osv):
    """modify account.invoice"""
    def onchange_installments_selection(self, cr, uid,ids,selected_installments):
        vals = {}
        total = 0
        for f in self.pool.get('client.trancations').browse(cr,uid,selected_installments[0][2]):
            total = total + f.amount
        vals['amount'] = total
                       
        return {'value':vals}
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        super(account_voucher, self).proforma_voucher(cr, uid, ids)
        for f in self.browse(cr,uid,ids):
            if f.installments:
                for inst_id in f.installments:
                    #            inst_ids = f.installments[0]
                    self.pool.get('client.trancations').write(cr,uid,inst_id.id,{'state':'Paid','paid_on':datetime.now(),'instalment_received_by':uid}) 
            else:
                raise osv.except_osv(('Already Posted To'),(str(f.installments)+" Register"))
        return True
    
    _name = 'account.voucher'
    _inherit = 'account.voucher'
    _columns = {
                 'installments': fields.many2many('client.trancations', 'instlament_account_voucher_rel', 'voucher_id', 'instalment_id', 'Installments to Pay', required=True, domain=[('state','=','Unpaid')]),
                }
account_voucher()         
                