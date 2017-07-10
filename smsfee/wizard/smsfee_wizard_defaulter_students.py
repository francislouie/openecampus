from openerp.osv import fields, osv
import datetime

class fee_defaulters(osv.osv_memory):

    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
    
    _name = "fee.defaulters"
    _description = "Prints defaulter list"
    _columns = {
              "session": fields.many2one('sms.session', 'Session', help="Select A session , you can also print reprts from previous session."),
              "class_id": fields.many2many('sms.academiccalendar','academiccalendar_class_fee','self_id','academiccalendar_id','Class',domain="[('session_id','=',session),('fee_defined','=',1)]"),
              'report_type': fields.selection([('summary','Print Summary (Donot show monthly Details'),('detailed','Detailed Report')],'Options'),
              'category':fields.selection([('Academics','Academics'),('Transport','Transport'),('All','All Fee Categories')],'Fee Category')
               }
    _defaults = {
                 'session':_get_active_session,
                 'category':'Academics',
           }
    
    def print_defaulter_summary(self, cr, uid, ids, data):
        result = []
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee_defaulter_studnent_list_name',
            'datas': datas,
        }
        
    def print_defaulter_detailed(self, cr, uid, ids, data):
        result = []
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee_annaul_defaulter_list_name',
            'datas': datas,
        }
                
fee_defaulters()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: