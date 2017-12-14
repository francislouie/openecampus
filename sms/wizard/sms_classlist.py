from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class sms_classlist_wizard(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "sms.classlist.wizard"
    _description = "Print student admitted in this class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', help="Class"),
              'class_form': fields.boolean('Class View'),
               }
    _defaults = {
                 'class_id':_get_class,
                 'class_form':True
                 }
    
    def print_class_list(self, cr, uid, ids, data):
        report = 'sms.class.list.name'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
            
sms_classlist_wizard()
