from openerp.osv import fields, osv
from datetime import date, datetime
import datetime
import time
import logging

class sms_mass(osv.osv):

    def set_to_waiting(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state':'Waiting'})
        return
    
    def set_to_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state':'Approved', 'action_date':datetime.date.today()})
        return
    
    _name="sms.mass"
    _columns = {
        'name':fields.char('Name', size=256),
        'subject' : fields.char('Subject', size=256),
        'state': fields.selection([('Draft', 'Draft'),('Waiting', 'Waiting'),('Approved','Approved'),('Sent','Sent')], 'State'),
        'student_id':fields.many2one('sms.student', 'Student'),
        'body':fields.text(string="Message Body"),
#        'sending_option':fields.many2one('opt.sending_options','Sending Option'),
        'composed_date':fields.date("Composed On"),
        'action_date':fields.date("Action Taken On"), #///this will be update when status changes from draft to any other......
            }
    _defaults = {
         'state':'Draft',
         'composed_date':lambda *a:time.strftime('%Y-%m-%d'),
         'action_date':lambda *a:time.strftime('%Y-%m-%d'),
            }
    
sms_mass()

# class sendingCarrierTable(osv.osv):
#     
#     _name="sms_mass.sendingCarrierTable"
#     _columns = {
#         'sms_id' : fields.char('Name', size=256),
#         'student_id': /////////////what to mention here basically i need to mention student id as  foriegn Key 
#         'action_date':fields.date("ATaken On"),
#         } 
# 
# sendingCarrierTable()

