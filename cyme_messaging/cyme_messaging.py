from openerp.osv import fields, osv
from datetime import date, datetime
import datetime
import time
import logging
import re

class mesg_main(osv.osv):
    
    def set_to_waiting(self, cr, uid, ids, context=None):
      
        return
    
    def set_to_approve(self, cr, uid, ids, context=None):
       
        return
    
    
    
    
    
    

    _name="mesg.main"
    _columns = {
        'title':fields.char('Title', size=256),
        'body':fields.text(string="Message Body"),
        'date_initiated':fields.datetime("Initiated date"),
        'initiated_by':fields.many2one('res.users', 'Initiated By'),
        'date_approved':fields.datetime("Approved date"),
        'approved_by':fields.many2one('res.users', 'Approved By'),
        'main_text':fields.text(string="Message Body"),
        'user_id':fields.many2one('res.users', 'User'),
        
        
       }
    _defaults = {
        
            }
    
mesg_main()


class mesg_lines(osv.osv):
    
    

    _name="mesg.lines"
    _columns = {
        
         'user_id':fields.many2one('res.users', 'User'),
         'message':fields.many2one('mesg.main', 'Message'),
         'date_mesg_delivery':fields.datetime("Mesg Delivery Date"),
         'state': fields.selection([('Sent', 'Sent'),('Delivered', 'Delivered'),('Failed','Failed')], 'State'),
        
       }
    _defaults = {
        
            }
    
mesg_lines()

class mesg_subscriber(osv.osv):
    
    
  

    def is_phone(self, cr, uid, ids, context=None):
            record = self.browse(cr, uid, ids)
            pattern ="^[0-9]{11}$"
            for data in record:
                print"record",data.phone
                if re.match(pattern, data.phone):
                    return True
                else:
                    return False
            return {}

    _name="mesg.subscriber"
    _columns = {
        
         'name':fields.char('Name', size=256),
         'phone':fields.char('phone'),
         'network': fields.selection([('Telenor', 'Telenor'),('Ufoun', 'Ufoun'),('Zong','Zong'),('Jazz','Jazz')], 'State'),
        
       }
    _defaults = {
        
            }
    _constraints = [(is_phone, 'Error: Invalid phone', ['phone']), ]
    
mesg_subscriber()

