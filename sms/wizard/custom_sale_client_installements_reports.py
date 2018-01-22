from openerp.osv import fields, osv
import datetime
import xlwt
import socket
import fcntl
import struct
from struct import pack, unpack

class cleint_instalment_history(osv.osv_memory):

    _name = "cleint.instalment.history"
    _description = "Client Transaction"
    _columns = {
              'client_':fields.many2one('res.partner','Client',domain = [('customer','=',True)] ),
              'invoice': fields.many2one('account.invoice','Invoice',domain = [('customer','=',True)] ),
              'start_date': fields.date('Start Date'),
              'end_date':fields.date('End Ddate'),
             }
    _defaults = { 
                 'start_date': '2007-06-07',
                 'end_date': '2016-06-09'
           }

    def print_list(self, cr, uid, ids, data):
        result = []
        thisform = self.browse(cr, uid, ids)[0]
        report = 'sale_invoice_print_receipt'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
cleint_instalment_history()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: